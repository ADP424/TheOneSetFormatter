from PIL import Image

from model.Layer import Layer


class Card:
    """
    A layered image representing a card and all the collection info on it.

    Attributes
    ----------
    base_width : int, default: 1500
        The width of the root image (typically the width of a Magic card, 1500px).

    base_height : int, default: 2100
        The height of the root image (typically the height of a Magic card, 2100px).

    layers : List[Layer], default: []
        The list of layers. Lower-index layers are rendered first.
    """

    def __init__(
        self,
        base_width: int = 1500,
        base_height: int = 2100,
        layers: list[Layer] = None
    ):
        self.base_width = base_width
        self.base_height = base_height
        self.layers = layers if layers is not None else []

    def add_layer(
        self,
        image: Image.Image | str,
        index: int = None,
        position: tuple[int, int] = (0, 0)
    ):
        """
        Add a layer with the image at the given path before the given index.

        Parameters
        ----------
        image: Image.Image | str
            The Image, or the path to the image, to set the layer to.

        index: int, optional
            The index to add the layer before. Adds to the top if not given.

        position: tuple[int, int], default: (0, 0)
            The position of the layer relative to the top left corner of the image.
        """

        if isinstance(image, str):
            image = Image.open(image)

        if index == None:
            self.layers.append(Layer(image, position))
        else:
            self.layers.insert(index, Layer(image, position))

    def remove_layer(self, index: int):
        """
        Remove the layer at the given index.

        Parameters
        ----------
        index: int
            The index of the layer to remove.
        """

        self.layers.pop(index)

    def merge_layers(self) -> Image.Image:
        """
        Merge all layers into one image.

        Returns
        -------
        Image
            The merged image. Returns None if the Card has no layers.
        """

        if len(self.layers) == 0:
            return None

        base_image = self.layers[0].image
        composite_image = base_image.copy()

        for layer in self.layers[1:]:
            composite_image.paste(layer.image, layer.position, mask=layer.image)

        return composite_image
