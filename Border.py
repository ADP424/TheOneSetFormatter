from PIL import Image


class Border:
    """
    A layered image representing a card's border and all the collection info on it.

    Attributes
    ----------
    base_width : int, default: 1500
        The width of the root image (typically the width of a Magic card, 1500px).

    base_height : int, default: 2100
        The height of the root image (typically the height of a Magic card, 2100px).

    layers : List[Image], default: []
        The list of images. Lower-index images are rendered first.
    """

    def __init__(
        self,
        base_width: int = 1500,
        base_height: int = 2100,
        layers: list[Image.Image] = None
    ):
        self.base_width = base_width
        self.base_height = base_height
        self.layers = layers if layers is not None else []

    def add_layer(
        self,
        image_path: str,
        index: int = None,
    ):
        """
        Add a layer with the image at the given path before the given index.

        Parameters
        ----------
        image_path: str
            The path of the image to set the layer to.

        index: int, optional
            The index to add the layer before. Adds to the top if not given.
        """

        image = Image.open(image_path)

        if index == None:
            self.layers.append(image)
        else:
            self.layers.insert(index, image)

    def merge_layers(self) -> Image.Image:
        """
        Merge all layers into one image.

        Returns
        -------
        Image
            The merged image.
        """

        base_layer = Image.open("images/base.png")
        composite_image = base_layer.copy()

        for layer in self.layers:
            composite_image.paste(layer, mask=layer)

        return composite_image
