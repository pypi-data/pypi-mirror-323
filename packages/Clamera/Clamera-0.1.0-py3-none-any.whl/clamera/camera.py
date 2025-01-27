import pygame

class Camera:
    """
    A versatile 2D camera system for top-down games using Pygame.

    Attributes:
        width (int): The width of the camera viewport.
        height (int): The height of the camera viewport.
        world_width (int): The width of the game world.
        world_height (int): The height of the game world.
        position (pygame.Vector2): The current position of the camera in world coordinates.
        zoom (float): The zoom level of the camera.
    """
    
    def __init__(self, viewport_width:int, viewport_height:int, min_zoom:float=0.1, max_zoom:float=None) -> None:
        """
        Initialize the camera viewport size (width, height) and zoom limits.
        
            Args:
                viewport_width, viewport_height: Dimentions of the camera viewport.

               min_zoom: Minimum allowable zoom level (default is 0.1).

               max_zoom: Maximum allowable zoom level (default is unlimited)
        """

        self.viewport = pygame.Rect(0 ,0, viewport_width, viewport_height)
        self.zoom = 1.0
        self.min_zoom = min_zoom
        self.max_zoom = max_zoom

    

    def set_position(self, position_x:int, position_y:int) -> None:
        """
        Set the position of the top-left of the viewport.

            Args: 
                position_x, position_y: New top left corner of the camera in world-space coordinates
        """

        self.viewport.topleft = (position_x, position_y)
    


    def apply(self, world_rect:pygame.Rect) -> pygame.Rect:
        """
        Convert a world-space rectangle to screen-space coordinates.

            Args: 
                world_rect: A pygame.Rect in world coordinates.

            Returns: 
                A pygame.Rect adjusted for both zoom and camera movement/positions.

        Note: world_rect must be in world coordinates.
        """

        if not isinstance(world_rect, pygame.Rect):
            raise TypeError("Expected world_rect to be a pygame.Rect")

        scaled_rect = pygame.Rect(
            world_rect.x * self.zoom,
            world_rect.y * self.zoom,
            world_rect.width * self.zoom,
            world_rect.height * self.zoom
        )

        return scaled_rect.move(-self.viewport.x * self.zoom, -self.viewport.y * self.zoom)
    


    def apply_point(self, world_point:tuple) -> tuple:
        """
        Convert a world-space point to screen-space coordinates.

            Args: 
                world_point: A tuple (x, y) in world-space coordinates.

            Returns:
                A tuple (x, y) addjusted for the camera's position and zoom.
        """
        
        if not (isinstance(world_point, tuple) and len(world_point) == 2):
            raise TypeError("Expected world_point to be a tuple of two numeric values")

        return (
            (world_point[0] - self.viewport.x) * self.zoom,
            (world_point[1] - self.viewport.y) * self.zoom
        )
    


    def zoom_in(self, zoom_factor) -> None:
        """
        Zoom in by multiplying the current zoom level by a factor.

            Args:
                zoom_factor: The factor by which to zoom in (e.g., 1.1 for 10%)
        """

        new_zoom = self.zoom * zoom_factor
        self._set_zoom(new_zoom)



    def zoom_out(self, zoom_factor) -> None:
        """
        Zoom out by dividing the current zoom level by a factor.

            Args:
                zoom_factor: The factor by which to zoom out (e.g., 1.1 for 10%)
        """

        new_zoom = self.zoom / zoom_factor
        self._set_zoom(new_zoom)



    def reset_zoom(self) -> None:
        """
        Reset the zoom value to the default (1.0).
        """

        self.zoom = 1.0



    def _set_zoom(self, zoom_level) -> None:
        """
        Internal method, sets the zoom to the current zoom_level.
        To be obtained by calling get_zoom().
        """

        if self.min_zoom is not None or self.max_zoom is not None:

            if self.min_zoom is not None:
                zoom_level = max(self.min_zoom, zoom_level)

            if self.max_zoom is not None:
                zoom_level = min(self.max_zoom, zoom_level)

        if zoom_level <= 0:
            raise ValueError("Zoom level must be greater than 0.")

        self.zoom = zoom_level



    def get_zoom(self) -> float:
        """
        Get the current zoom level.

        Returns:
            A float that represents the current zoom level.
        """

        return self.zoom
    


    def is_visible(self, world_rect:pygame.Rect) -> bool:
        """
        Check if a world-space rectangle is visible within the viewport.

            Args: 
                world_rect: A pygame.Rect in world coordinates

            Returns: 
                True if the rectangle is at least partially visible
        """

        if not isinstance(world_rect, pygame.Rect):
            raise TypeError("Expected world_rect to be a pygame.Rect")

        visible_area = self.get_visible_area()
        return visible_area.colliderect(world_rect)



    def get_visible_area(self) -> pygame.Rect:
        """
        Get bounds of the visible area in world-space.

            Returns: A pygame.Rect that represents the parts of a map visible in the viewport.
        """

        viewport_width = int(self.viewport.width / self.zoom)
        viewport_height = int(self.viewport.height / self.zoom)
        
        return pygame.Rect(
            int(self.viewport.x),
            int(self.viewport.y),
            viewport_width,
            viewport_height
        )



    def scale_rect(self, rect) -> pygame.Rect:
        """
        Scale a world-space rectangle without translating it into screen-space.

            Args:
                rect: A pygame.Rect in world-space.

            Returns:
                A pygame.Rect scaled in world-space.
        """

        if not isinstance(rect, pygame.Rect):
            raise TypeError("Expected rect to be a pygame.Rect")

        return pygame.Rect(
            rect.x * self.zoom,
            rect.y * self.zoom,
            rect.width * self.zoom,
            rect.height * self.zoom
        )
    


    def scale_point(self, point) -> tuple:
        """
        Scale a world-space point without translating it to screen-space.

            Args:
                point: A tuple (x, y) in world-space coordinates.

            Returns:
                A point scaled in wolrd-space.
        """

        if not (isinstance(point, tuple) and len(point) == 2):
            raise TypeError("Expected point to be a tuple of two numeric values")

        return (point[0] * self.zoom, point[1] * self.zoom)