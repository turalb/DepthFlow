"""
(c) CC BY-SA 4.0, Tremeschin

Basic example of defining your own class based on DepthScene, running
it via CLI or a code managing it for automation

• For more information, visit https://brokensrc.dev/depthflow
"""
import math
import sys

from DepthFlow import DepthScene
from ShaderFlow.Message import ShaderMessage

# Note: DepthScene.method(self) is preferred over super().method(self) for clarity

class YourScene(DepthScene):

    def __init__(self):
        super().__init__()

    def map_to_range(x):
            """Maps a number from [0, 2*pi] to [0, 10]."""
            return (10 / (2 * math.pi)) * x

    @staticmethod
    def map_sine_to_range(cycle, a, b):
        """Maps sin(cycle) from [-1,1] to [a,b] where 0 <= a < b <= 1."""
        return a + ((b - a) / 2) * (math.sin(cycle) + 1)


    def sine_based_zoom(cycle: float, z: float) -> float:
        """
        Maps a cycle (0 to 2*pi) to a zoom level between 1 and z using a cosine function.

        Args:
            cycle (float): The current cycle value (0 to 2*pi).
            z (float): The minimum zoom level (e.g., 0.6).

        Returns:
            float: The zoom value.
        """
        return (1 - z) / 2 * math.cos(cycle) + (1 + z) / 2


    def convert_to_depthflow_coords(x_pixel, y_pixel, img_width, img_height, range_min=-5, range_max=5):
        """
        Convert pixel coordinates (x_pixel, y_pixel) to DepthFlow coordinates within a custom range.

        :param x_pixel: X coordinate in pixel space (0-based).
        :param y_pixel: Y coordinate in pixel space (0-based).
        :param img_width: Width of the image in pixels.
        :param img_height: Height of the image in pixels.
        :param range_min: Minimum value of the DepthFlow coordinate range.
        :param range_max: Maximum value of the DepthFlow coordinate range.
        :return: (center_x, center_y) mapped to the specified range.
        """
        scale = range_max - range_min  # Determine the mapping scale

        center_x = (x_pixel / (img_width - 1)) * scale + range_min  # Map [0, img_width-1] to [range_min, range_max]
        center_y = (1 - (y_pixel / (img_height - 1))) * scale + range_min  # Map [0, img_height-1] to [range_min, range_max]

        return center_x, center_y


    def animation_full_view_no_zoom_move_xy_use_iso(self):
        # Set the fixed values first
        self.state.steady = 1
        self.state.focus = 0
        self.state.mirror = True  # Enable mirroring for effects
        self.state.height = 0.4
        self.state.invert = 0.35

        self.state.offset_x = 0.5 * math.sin(self.cycle)
        self.state.offset_y = 0.5 * math.cos(self.cycle)

        # Setting isometric only works if there is some height set
        self.state.isometric = YourScene.map_sine_to_range(self.cycle, 0, 1)


    def animation_full_view_no_zoom_move_x_only_use_iso(self):
        # Set the fixed values first
        self.state.steady = 1
        self.state.focus = 0
        self.state.mirror = True  # Enable mirroring for effects
        self.state.height = 0.4
        self.state.invert = 0.35

        self.state.offset_x = 0.5 * math.sin(self.cycle)

        # Setting isometric only works if there is some height set
        self.state.isometric = YourScene.map_sine_to_range(self.cycle, 0, 1)


    def animation_zoomed(self, box_center_x, box_center_y, img_width, img_height):
        origin_x, origin_y = YourScene.convert_to_depthflow_coords(box_center_x, box_center_y, img_width, img_height)

        # origin_x, origin_y = -10, -10
        # origin_x, origin_y = 0.353, -0.26
        # 0.103, -0.63
        # Set the fixed values first
        self.state.steady = 1
        self.state.focus = 0
        self.state.mirror = True  # Enable mirroring for effects
        self.state.invert = 0.35

        self.state.origin_x = origin_x
        self.state.origin_y = origin_y

        self.state.zoom = 0.5

        self.state.offset_x = 0.5 * math.sin(self.cycle)
        # self.state.offset_y = 0.5 * math.cos(self.cycle)


    def update(self):
        # self.animation_full_view_no_zoom_move_xy_use_iso()
        self.animation_zoomed(595.5, 1565.0, 1400, 2100)
        # self.animation_zoomed(731.0, 1214.0, 1400, 2100)


    def pipeline(self):
        yield from DepthScene.pipeline(self)
        ...

    def handle(self, message: ShaderMessage):
        DepthScene.handle(self, message)
        ...

def manual():
    scene = YourScene()
    scene.cli(sys.argv[1:])

def managed():
    from Broken.Externals.Upscaler import Realesr
    # Note: For headless rendering / server, use backend='headless'
    scene = YourScene(backend="glfw")
    scene.set_upscaler(Realesr())
    scene.input(image="image.png")
    scene.main(output="./video.mp4", fps=30, time=5)
    scene.window.destroy()

if __name__ == "__main__":
    # managed()
    manual()
