from datetime import datetime
from typing import List

import pandas as pd
import numpy as np
from cag.framework import GenericAnnotator

from conf import config


class MovieEmbeddingsCreator(GenericAnnotator):
    """
    A class to create fake embeddings for movie titles and descriptions.

    Attributes:
        config (dict): A dictionary containing configuration settings.
        run (bool): A flag indicating whether to run the annotator.

    Methods:
        generate_fake_embedding(data: List[str]) -> List:
            Generates a list of fake embeddings for the input text data.

        update_graph(timestamp=datetime.now(), data=None) -> None:
            Updates the ArangoDB graph database with fake embeddings for movie titles and descriptions.
    """

    def __init__(self, config, run=False):
        super().__init__(conf=config, query=None, run=run)

    @staticmethod
    def generate_fake_embedding(data: List[str]):
        """
        Generates a list of fake embeddings for the input text data.

        Args:
            data (List[str]): A list of strings containing the text data.

        Returns:
            List: A list of fake embeddings for the input text data.
        """
        return [np.random.rand(len(text.split()), 50) for text in data]

    def update_graph(self, timestamp=datetime.now(), data=None):
        """
        Updates the ArangoDB graph database with fake embeddings for movie titles and descriptions.

        Args:
           timestamp (datetime): A datetime object indicating the timestamp for the update.
               Default is the current datetime.
           data: Unused.

        Returns:
           None
        """
        self.query = """
                    FOR movie in Movie
                        FILTER !HAS(movie, "title_emb") and movie.title!=null
                        FILTER !HAS(movie, "description_emb") and movie.description!=null
                        RETURN {_id:movie._id,title:movie.title, description:movie.description}
                    """
        batch_size = 512
        # note: we do manual paging count, may not be stable!
        total_count = self.query_count()
        if total_count == 0:
            print("No Movies found that have no embeddings...")
            return
        print(f"Starting job, total docs: {total_count}")
        ds_collection = self.arango_db["Movie"]

        for i in range(0, total_count, batch_size):
            batch = self.load_page(i, batch_size)
            dataset_batch = list(batch)
            datasets_df_batch = pd.DataFrame(dataset_batch)
            if (
                datasets_df_batch.empty
            ):  # as said, manual batching is sometimes error-prone
                continue
            title_batch = datasets_df_batch.title.tolist()

            description_batch = datasets_df_batch.description.tolist()

            title_embs = self.generate_fake_embedding(title_batch)
            ab_embs = self.generate_fake_embedding(description_batch)

            datasets_df_batch.loc[:, "title_emb"] = list(title_embs)
            datasets_df_batch.loc[:, "description_emb"] = list(ab_embs)
            datasets_df_batch["title_emb"] = datasets_df_batch["title_emb"].apply(
                lambda x: x.squeeze().tolist()
            )
            datasets_df_batch["description_emb"] = datasets_df_batch[
                "description_emb"
            ].apply(lambda x: x.squeeze().tolist())
            update_batch = datasets_df_batch.loc[
                :, ["_id", "title_emb", "description_emb"]
            ].to_dict("records")
            ds_collection.update_many(update_batch)


if __name__ == "__main__":
    """
    Main script to create fake movie embeddings.

    Args:
        None

    Returns:
        None
    """
    emb_creator = MovieEmbeddingsCreator(config)
    emb_creator.update_graph()
