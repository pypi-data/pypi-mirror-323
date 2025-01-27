from .utils import helper_functions as hf
import click


@click.command()
def main():

    hf.install_exiftool()

    src, dst = hf.locations()

    folder_structure = hf.folder_structure()

    pfd = hf.get_pfd(src)

    # print(pfd)

    hf.mkdir_tool(folder_structure=folder_structure, pfd=pfd, dst=dst)

    hf.copy_and_rename(src=src, dst=dst, pfd=pfd, folder_structure=folder_structure)


if __name__ == "__main__":
    main()
