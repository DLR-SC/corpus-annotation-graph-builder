import examples.annotation_example
from cag.utils.config import Config

def main():
    config= Config(
        url="http://127.0.0.1:8529",
        user="root",
        password="root",
        database="_system",
        graph="GenericGraph"
    )

    examples.annotation_example.run_sample(config)



if __name__ == "__main__":
    main()