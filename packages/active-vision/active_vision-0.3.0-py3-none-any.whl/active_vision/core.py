import pandas as pd
from loguru import logger
from fastai.vision.all import *
import torch
import numpy as np
import bisect

import warnings
from typing import Callable

warnings.filterwarnings("ignore", category=FutureWarning)


class ActiveLearner:
    """
    Active Learning framework for computer vision tasks.

    Attributes:
        Model Related:
            model: The base model architecture (str or Callable)
            learn: fastai Learner object for training
            lrs: Learning rate finder results

        Data Related:
            train_set (pd.DataFrame): Training dataset
            eval_set (pd.DataFrame): Evaluation dataset with ground truth labels
            dls: fastai DataLoaders object
            class_names: List of class names from the dataset
            num_classes (int): Number of classes in the dataset

        Prediction Related:
            pred_df (pd.DataFrame): Predictions on a dataframe
            eval_df (pd.DataFrame): Predictions on evaluation data
    """

    def __init__(self, model_name: str | Callable):
        self.model = self.load_model(model_name)

    def load_model(self, model_name: str | Callable):
        if isinstance(model_name, Callable):
            logger.info(f"Loading fastai model {model_name.__name__}")
            return model_name

        if isinstance(model_name, str):
            logger.info(f"Loading timm model {model_name}")
            return model_name

    def load_dataset(
        self,
        df: pd.DataFrame,
        filepath_col: str,
        label_col: str,
        valid_pct: float = 0.2,
        batch_size: int = 16,
        image_size: int = 224,
        batch_tfms: Callable = None,
        learner_path: str = None,
    ):
        logger.info(f"Loading dataset from {filepath_col} and {label_col}")

        logger.info("Creating dataloaders")
        self.dls = ImageDataLoaders.from_df(
            df,
            path=".",
            valid_pct=valid_pct,
            fn_col=filepath_col,
            label_col=label_col,
            bs=batch_size,
            item_tfms=Resize(image_size),
            batch_tfms=batch_tfms,
        )

        if learner_path:
            logger.info(f"Loading learner from {learner_path}")
            gpu_available = torch.cuda.is_available()
            if gpu_available:
                logger.info(f"Loading learner on GPU.")
            else:
                logger.info(f"Loading learner on CPU.")

            self.learn = load_learner(learner_path, cpu=not gpu_available)
        else:
            logger.info("Creating learner")
            self.learn = vision_learner(
                self.dls, self.model, metrics=accuracy
            ).to_fp16()

        self.train_set = self.learn.dls.train_ds.items
        self.valid_set = self.learn.dls.valid_ds.items
        self.class_names = self.dls.vocab
        self.num_classes = self.dls.c
        logger.info("Done. Ready to train.")

    def show_batch(
        self,
        num_samples: int = 9,
        unique: bool = False,
        num_rows: int = None,
        num_cols: int = None,
    ):
        """
        Show a batch of images from the dataset.

        Args:
            num_samples: Number of samples to show.
            unique: Whether to show unique samples.
            num_rows: Number of rows in the grid.
            num_cols: Number of columns in the grid.
        """
        self.dls.show_batch(
            max_n=num_samples, unique=unique, nrows=num_rows, ncols=num_cols
        )

    def lr_find(self):
        logger.info("Finding optimal learning rate")
        self.lrs = self.learn.lr_find(suggest_funcs=(minimum, steep, valley, slide))
        logger.info(f"Optimal learning rate: {self.lrs.valley}")

    def train(self, epochs: int, lr: float, head_tuning_epochs: int = 1):
        """
        Train the model.

        Args:
            epochs: Number of epochs to train for.
            lr: Learning rate.
            head_tuning_epochs: Number of epochs to train the head.
        """
        logger.info(f"Training head for {head_tuning_epochs} epochs")
        logger.info(f"Training model end-to-end for {epochs} epochs")
        logger.info(f"Learning rate: {lr} with one-cycle learning rate scheduler")
        self.learn.fine_tune(
            epochs, lr, freeze_epochs=head_tuning_epochs, cbs=[ShowGraphCallback()]
        )

    def predict(self, filepaths: list[str], batch_size: int = 16):
        """
        Run inference on an unlabeled dataset. Returns a df with filepaths and predicted labels, and confidence scores.
        """
        logger.info(f"Running inference on {len(filepaths)} samples")
        test_dl = self.dls.test_dl(filepaths, bs=batch_size)

        def identity(x):
            return x

        logits, _, class_idxs = self.learn.get_preds(
            dl=test_dl, with_decoded=True, act=identity
        )

        self.pred_df = pd.DataFrame(
            {
                "filepath": filepaths,
                "pred_label": [self.learn.dls.vocab[i] for i in class_idxs.numpy()],
                "pred_conf": torch.max(F.softmax(logits, dim=1), dim=1)[0].numpy(),
                "probs": F.softmax(logits, dim=1).numpy().tolist(),
                "logits": logits.numpy().tolist(),
            }
        )

        return self.pred_df

    def evaluate(
        self, df: pd.DataFrame, filepath_col: str, label_col: str, batch_size: int = 16
    ):
        """
        Evaluate on a labeled dataset. Returns a score.
        """
        self.eval_set = df.copy()

        filepaths = self.eval_set[filepath_col].tolist()
        labels = self.eval_set[label_col].tolist()
        test_dl = self.dls.test_dl(filepaths, bs=batch_size)
        preds, _, cls_preds = self.learn.get_preds(dl=test_dl, with_decoded=True)

        self.eval_df = pd.DataFrame(
            {
                "filepath": filepaths,
                "label": labels,
                "pred_label": [self.learn.dls.vocab[i] for i in cls_preds.numpy()],
            }
        )

        accuracy = float((self.eval_df["label"] == self.eval_df["pred_label"]).mean())
        logger.info(f"Accuracy: {accuracy:.2%}")
        return accuracy

    def sample_uncertain(
        self, df: pd.DataFrame, num_samples: int, strategy: str = "least-confidence"
    ):
        """
        Sample top `num_samples` low confidence samples. Returns a df with filepaths and predicted labels, and confidence scores.

        Strategies:
        - least-confidence: Get top `num_samples` low confidence samples.
        - margin-of-confidence: Get top `num_samples` samples with the smallest margin between the top two predictions.
        - ratio-of-confidence: Get top `num_samples` samples with the highest ratio between the top two predictions.
        - entropy: Get top `num_samples` samples with the highest entropy.
        """

        # Remove samples that is already in the training set
        df = df[~df["filepath"].isin(self.train_set["filepath"])].copy()

        if strategy == "least-confidence":
            logger.info(
                f"Using least confidence strategy to get top {num_samples} samples"
            )
            df.loc[:, "score"] = 1 - (df["pred_conf"]) / (
                self.num_classes - (self.num_classes - 1)
            )

        elif strategy == "margin-of-confidence":
            logger.info(
                f"Using margin of confidence strategy to get top {num_samples} samples"
            )
            if len(df["probs"].iloc[0]) < 2:
                logger.error("probs has less than 2 elements")
                raise ValueError("probs has less than 2 elements")

            # Calculate uncertainty score as 1 - (difference between top two predictions)
            df.loc[:, "score"] = df["probs"].apply(
                lambda x: 1 - (np.sort(x)[-1] - np.sort(x)[-2])
            )

        elif strategy == "ratio-of-confidence":
            logger.info(
                f"Using ratio of confidence strategy to get top {num_samples} samples"
            )
            if len(df["probs"].iloc[0]) < 2:
                logger.error("probs has less than 2 elements")
                raise ValueError("probs has less than 2 elements")

            # Calculate uncertainty score as ratio of top two predictions
            df.loc[:, "score"] = df["probs"].apply(
                lambda x: np.sort(x)[-2] / np.sort(x)[-1]
            )

        elif strategy == "entropy":
            logger.info(f"Using entropy strategy to get top {num_samples} samples")

            # Calculate uncertainty score as entropy of the prediction
            df.loc[:, "score"] = df["probs"].apply(lambda x: -np.sum(x * np.log2(x)))

            # Normalize the uncertainty score to be between 0 and 1 by dividing by log2 of the number of classes
            df.loc[:, "score"] = df["score"] / np.log2(self.num_classes)

        else:
            logger.error(f"Unknown strategy: {strategy}")
            raise ValueError(f"Unknown strategy: {strategy}")

        df = df[["filepath", "pred_label", "pred_conf", "score", "probs", "logits"]]

        df["score"] = df["score"].map("{:.4f}".format)
        df["pred_conf"] = df["pred_conf"].map("{:.4f}".format)

        return df.sort_values(by="score", ascending=False).head(num_samples)

    def sample_diverse(
        self, df: pd.DataFrame, num_samples: int, strategy: str = "model-based-outlier"
    ):
        """
        Sample top `num_samples` diverse samples. Returns a df with filepaths and predicted labels, and confidence scores.

        Strategies:
        - model-based-outlier: Get top `num_samples` samples with lowest activation of the model's last layer.
        - cluster-based: Get top `num_samples` samples with the highest distance to the nearest neighbor.
        - representative: Get top `num_samples` samples with the highest distance to the centroid of the training set.

        """
        # Remove samples that is already in the training set
        df = df[~df["filepath"].isin(self.train_set["filepath"])].copy()

        if strategy == "model-based-outlier":
            logger.info(
                f"Using model-based outlier strategy to get top {num_samples} samples"
            )

            # Get the activations for all items in the validation set.
            valid_set_preds = self.predict(self.valid_set["filepath"].tolist())

            # Store logits for each class in a list instead of dict
            validation_class_logits = [
                sorted(
                    valid_set_preds["logits"].apply(lambda x: x[i]).tolist(),
                    reverse=True,
                )
                for i in range(self.num_classes)
            ]

            # Get the logits for the unlabeled set
            unlabeled_set_preds = self.predict(df["filepath"].tolist())

            # For each element in the unlabeled set logits, compare it to the validation set ranked logits and get the position in the ranked logits
            unlabeled_set_logits = []
            for idx, row in unlabeled_set_preds.iterrows():
                logits = row["logits"]
                # For each class, find where this sample's logit would rank in the validation set
                ranks = []
                for class_idx in range(self.num_classes):
                    class_logit = logits[class_idx]
                    ranked_logits = validation_class_logits[
                        class_idx
                    ]  # Access by index instead of dict key
                    # Find position where this logit would be inserted to maintain sorted order
                    # Now using bisect_left directly since logits are sorted high to low
                    rank = bisect.bisect_left(ranked_logits, class_logit)
                    ranks.append(
                        rank / len(ranked_logits)
                    )  # Normalize rank to 0-1 range

                # Average rank across all classes - lower means more outlier-like
                avg_rank = np.mean(ranks)
                unlabeled_set_logits.append(avg_rank)

            # Add outlier scores to dataframe
            df.loc[:, "score"] = unlabeled_set_logits

            df = df[["filepath", "pred_label", "pred_conf", "score", "probs", "logits"]]

            df["score"] = df["score"].map("{:.4f}".format)
            df["pred_conf"] = df["pred_conf"].map("{:.4f}".format)

            # Sort by score ascending higher rank = more outlier-like compared to the validation set
            return df.sort_values(by="score", ascending=False).head(num_samples)

    def sample_random(self, df: pd.DataFrame, num_samples: int, seed: int = None):
        """
        Sample `num_samples` random samples. Returns a df with filepaths and predicted labels, and confidence scores.
        """

        logger.info(f"Sampling {num_samples} random samples")
        if seed is not None:
            logger.info(f"Using seed: {seed}")
        return df.sample(n=num_samples, random_state=seed)

    def label(self, df: pd.DataFrame, output_filename: str = "labeled"):
        """
        Launch a labeling interface for the user to label the samples.
        Input is a df with filepaths listing the files to be labeled. Output is a df with filepaths and labels.
        """
        import gradio as gr

        shortcut_js = """
        <script>
        function shortcuts(e) {
            // Only block shortcuts if we're in a text input or textarea
            if (e.target.tagName.toLowerCase() === "textarea" || 
                (e.target.tagName.toLowerCase() === "input" && e.target.type.toLowerCase() === "text")) {
                return;
            }
            
            if (e.key === "ArrowUp") {
                document.getElementById("submit_btn").click();
            } else if (e.key === "ArrowRight") {
                document.getElementById("next_btn").click();
            } else if (e.key === "ArrowLeft") {
                document.getElementById("back_btn").click();
            }
        }
        document.addEventListener('keydown', shortcuts, false);
        </script>
        """

        logger.info(f"Launching labeling interface for {len(df)} samples")

        filepaths = df["filepath"].tolist()

        with gr.Blocks(head=shortcut_js) as demo:
            with gr.Tabs():
                with gr.Tab("Labeling"):
                    current_index = gr.State(value=0)

                    with gr.Row(min_height=500):
                        image = gr.Image(
                            type="filepath",
                            label="Image",
                            value=filepaths[0],
                            height=510,
                        )

                        # Add bar plot with top 5 predictions
                        with gr.Column():
                            pred_plot = gr.BarPlot(
                                x="probability",
                                y="class",
                                title="Top 5 Predictions",
                                x_lim=[0, 1],
                                value=None
                                if "probs" not in df.columns
                                else pd.DataFrame(
                                    {
                                        "class": self.class_names,
                                        "probability": df["probs"].iloc[0],
                                    }
                                ).nlargest(5, "probability"),
                            )

                            filename = gr.Textbox(
                                label="Filename", value=filepaths[0], interactive=False
                            )
                            with gr.Row():
                                pred_label = gr.Textbox(
                                    label="Predicted Label",
                                    value=df["pred_label"].iloc[0]
                                    if "pred_label" in df.columns
                                    else "",
                                    interactive=False,
                                )

                                pred_conf = gr.Textbox(
                                    label="Confidence",
                                    value=df["pred_conf"].iloc[0]
                                    if "pred_conf" in df.columns
                                    else "",
                                    interactive=False,
                                )

                            sample_score = gr.Textbox(
                                label="Sample Score [0-1] - Indicates how informative the sample is. Higher means more informative.",
                                value=df["score"].iloc[0]
                                if "score" in df.columns
                                else "",
                                interactive=False,
                            )

                    category = gr.Radio(
                        choices=self.class_names,
                        label="Select Category",
                        value=df["pred_label"].iloc[0]
                        if "pred_label" in df.columns
                        else None,
                    )

                    with gr.Row():
                        back_btn = gr.Button("← Previous", elem_id="back_btn")
                        submit_btn = gr.Button(
                            "Submit ↑",
                            variant="primary",
                            elem_id="submit_btn",
                        )
                        next_btn = gr.Button("Next →", elem_id="next_btn")

                    progress = gr.Slider(
                        minimum=0,
                        maximum=len(filepaths) - 1,
                        value=0,
                        step=1,
                        label="Progress",
                        interactive=True,
                    )

                    # Add event handler for slider changes
                    progress.change(
                        fn=lambda idx: navigate(idx, 0),
                        inputs=[progress],
                        outputs=[
                            filename,
                            image,
                            pred_label,
                            pred_conf,
                            category,
                            current_index,
                            progress,
                            pred_plot,
                            sample_score,
                        ],
                    )

                    finish_btn = gr.Button("Finish Labeling", variant="primary")

                with gr.Tab("Zero-Shot Inference"):
                    gr.Markdown("""
                    Uses a VLM to predict the label of the image.
                    """)

                    import xinfer
                    from xinfer.model_registry import model_registry
                    from xinfer.types import ModelInputOutput

                    # Get models and filter for image-to-text models
                    all_models = model_registry.list_models()
                    model_list = [
                        model.id
                        for model in all_models
                        if model.input_output == ModelInputOutput.IMAGE_TEXT_TO_TEXT
                    ]

                    with gr.Row():
                        with gr.Row():
                            model_dropdown = gr.Dropdown(
                                choices=model_list,
                                label="Select a model",
                                value="vikhyatk/moondream2",
                            )
                            device_dropdown = gr.Dropdown(
                                choices=["cuda", "cpu"],
                                label="Device",
                                value="cuda" if torch.cuda.is_available() else "cpu",
                            )
                            dtype_dropdown = gr.Dropdown(
                                choices=["float32", "float16", "bfloat16"],
                                label="Data Type",
                                value="float16"
                                if torch.cuda.is_available()
                                else "float32",
                            )

                    with gr.Column():
                        prompt_textbox = gr.Textbox(
                            label="Prompt",
                            lines=5,
                            value=f"Classify the image into one of the following categories: {self.class_names}. Answer with the category name only.",
                            interactive=True,
                        )
                        inference_btn = gr.Button("Run Inference", variant="primary")

                        result_textbox = gr.Textbox(
                            label="Result",
                            lines=3,
                            interactive=False,
                        )

            def run_zero_shot_inference(prompt, model, device, dtype, current_filename):
                model = xinfer.create_model(model, device=device, dtype=dtype)
                result = model.infer(current_filename, prompt).text
                return result

            inference_btn.click(
                fn=run_zero_shot_inference,
                inputs=[
                    prompt_textbox,
                    model_dropdown,
                    device_dropdown,
                    dtype_dropdown,
                    filename,
                ],
                outputs=[result_textbox],
            )

            def update_submit_btn(choice):
                return gr.Button(interactive=choice is not None)

            category.change(
                fn=update_submit_btn, inputs=[category], outputs=[submit_btn]
            )

            def navigate(current_idx, direction):
                # Convert current_idx to int before arithmetic
                current_idx = int(current_idx)
                next_idx = current_idx + direction

                if 0 <= next_idx < len(filepaths):
                    plot_data = (
                        None
                        if "probs" not in df.columns
                        else pd.DataFrame(
                            {
                                "class": self.class_names,
                                "probability": df["probs"].iloc[next_idx],
                            }
                        ).nlargest(5, "probability")
                    )
                    return (
                        filepaths[next_idx],
                        filepaths[next_idx],
                        df["pred_label"].iloc[next_idx]
                        if "pred_label" in df.columns
                        else "",
                        df["pred_conf"].iloc[next_idx]
                        if "pred_conf" in df.columns
                        else "",
                        df["pred_label"].iloc[next_idx]
                        if "pred_label" in df.columns
                        else None,
                        next_idx,
                        next_idx,
                        plot_data,
                        df["score"].iloc[next_idx] if "score" in df.columns else "",
                    )
                plot_data = (
                    None
                    if "probs" not in df.columns
                    else pd.DataFrame(
                        {
                            "class": self.class_names,
                            "probability": df["probs"].iloc[current_idx],
                        }
                    ).nlargest(5, "probability")
                )
                return (
                    filepaths[current_idx],
                    filepaths[current_idx],
                    df["pred_label"].iloc[current_idx]
                    if "pred_label" in df.columns
                    else "",
                    df["pred_conf"].iloc[current_idx]
                    if "pred_conf" in df.columns
                    else "",
                    df["pred_label"].iloc[current_idx]
                    if "pred_label" in df.columns
                    else None,
                    current_idx,
                    current_idx,
                    plot_data,
                    df["score"].iloc[current_idx] if "score" in df.columns else "",
                )

            def save_and_next(current_idx, selected_category):
                # Convert current_idx to int before arithmetic
                current_idx = int(current_idx)

                if selected_category is None:
                    plot_data = (
                        None
                        if "probs" not in df.columns
                        else pd.DataFrame(
                            {
                                "class": self.class_names,
                                "probability": df["probs"].iloc[current_idx],
                            }
                        ).nlargest(5, "probability")
                    )
                    return (
                        filepaths[current_idx],
                        filepaths[current_idx],
                        df["pred_label"].iloc[current_idx]
                        if "pred_label" in df.columns
                        else "",
                        df["pred_conf"].iloc[current_idx]
                        if "pred_conf" in df.columns
                        else "",
                        df["pred_label"].iloc[current_idx]
                        if "pred_label" in df.columns
                        else None,
                        current_idx,
                        current_idx,
                        plot_data,
                        df["score"].iloc[current_idx] if "score" in df.columns else "",
                    )

                # Save the current annotation
                with open(f"{output_filename}.csv", "a") as f:
                    f.write(f"{filepaths[current_idx]},{selected_category}\n")

                # Move to next image if not at the end
                next_idx = current_idx + 1
                if next_idx >= len(filepaths):
                    plot_data = (
                        None
                        if "probs" not in df.columns
                        else pd.DataFrame(
                            {
                                "class": self.class_names,
                                "probability": df["probs"].iloc[current_idx],
                            }
                        ).nlargest(5, "probability")
                    )
                    return (
                        filepaths[current_idx],
                        filepaths[current_idx],
                        df["pred_label"].iloc[current_idx]
                        if "pred_label" in df.columns
                        else "",
                        df["pred_conf"].iloc[current_idx]
                        if "pred_conf" in df.columns
                        else "",
                        df["pred_label"].iloc[current_idx]
                        if "pred_label" in df.columns
                        else None,
                        current_idx,
                        current_idx,
                        plot_data,
                        df["score"].iloc[current_idx] if "score" in df.columns else "",
                    )

                plot_data = (
                    None
                    if "probs" not in df.columns
                    else pd.DataFrame(
                        {
                            "class": self.class_names,
                            "probability": df["probs"].iloc[next_idx],
                        }
                    ).nlargest(5, "probability")
                )
                return (
                    filepaths[next_idx],
                    filepaths[next_idx],
                    df["pred_label"].iloc[next_idx]
                    if "pred_label" in df.columns
                    else "",
                    df["pred_conf"].iloc[next_idx] if "pred_conf" in df.columns else "",
                    df["pred_label"].iloc[next_idx]
                    if "pred_label" in df.columns
                    else None,
                    next_idx,
                    next_idx,
                    plot_data,
                    df["score"].iloc[next_idx] if "score" in df.columns else "",
                )

            def convert_csv_to_parquet():
                try:
                    df = pd.read_csv(f"{output_filename}.csv", header=None)
                    df.columns = ["filepath", "label"]
                    df = df.drop_duplicates(subset=["filepath"], keep="last")
                    df.to_parquet(f"{output_filename}.parquet")
                    gr.Info(f"Annotation saved to {output_filename}.parquet")
                except Exception as e:
                    logger.error(e)
                    return

            back_btn.click(
                fn=lambda idx: navigate(idx, -1),
                inputs=[current_index],
                outputs=[
                    filename,
                    image,
                    pred_label,
                    pred_conf,
                    category,
                    current_index,
                    progress,
                    pred_plot,
                    sample_score,
                ],
            )

            next_btn.click(
                fn=lambda idx: navigate(idx, 1),
                inputs=[current_index],
                outputs=[
                    filename,
                    image,
                    pred_label,
                    pred_conf,
                    category,
                    current_index,
                    progress,
                    pred_plot,
                    sample_score,
                ],
            )

            submit_btn.click(
                fn=save_and_next,
                inputs=[current_index, category],
                outputs=[
                    filename,
                    image,
                    pred_label,
                    pred_conf,
                    category,
                    current_index,
                    progress,
                    pred_plot,
                    sample_score,
                ],
            )

            finish_btn.click(fn=convert_csv_to_parquet)

        demo.launch(height=1000)

    def add_to_train_set(self, df: pd.DataFrame, output_filename: str):
        """
        Add samples to the training set.
        """
        new_train_set = df.copy()

        logger.info(f"Adding {len(new_train_set)} samples to training set")
        self.train_set = pd.concat([self.train_set, new_train_set])

        self.train_set = self.train_set.drop_duplicates(
            subset=["filepath"], keep="last"
        )
        self.train_set.reset_index(drop=True, inplace=True)

        self.train_set.to_parquet(f"{output_filename}.parquet")
        logger.info(f"Saved training set to {output_filename}.parquet")
