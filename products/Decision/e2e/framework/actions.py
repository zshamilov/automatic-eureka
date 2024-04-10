from time import time, sleep
from typing import Union
from playwright.sync_api import Locator


def wait_for_stable(element, timeout=1, period=0.5) -> bool:
    starting_size = element.bounding_box()
    now = time()
    while time() < now + timeout:
        sleep(period)
        if starting_size == element.bounding_box():
            return True
        starting_size = element.bounding_box()
    return False


def pick_from_dropdown_menu(page, element, menu_option: Union[Locator, None] = None) -> None:
    if element.is_visible():
        element.click()
    else:
        menu_option.hover()
        page.mouse.wheel(delta_x=400, delta_y=400)
        element.scroll_into_view_if_needed()
        element.click()


def link_nodes(page, from_node, to_node) -> None:
    from_node.hover()
    page.mouse.down()
    dest_elem_boundary = to_node.bounding_box()
    page.mouse.move(x=dest_elem_boundary["x"] + dest_elem_boundary['width'] / 1.1,
                    y=dest_elem_boundary["y"] + dest_elem_boundary["height"] / 1.1)
    page.mouse.up()


def drag_n_drop(page, element, to, x_scale=1.2, y_scale=1) -> None:
    element.scroll_into_view_if_needed()
    element.hover()

    page.mouse.down()

    src_bounding_box = element.bounding_box()
    src_x = src_bounding_box['x']
    src_y = src_bounding_box['y']
    for i in range(3):
        page.mouse.move(
            src_x + 100 * (-1) ** i,
            src_y + 100 * (-1) ** i
        )

    dst_bounding_box = to.bounding_box()
    page.mouse.move(
        dst_bounding_box['x'] + dst_bounding_box['width'] * x_scale,
        dst_bounding_box['y'] + dst_bounding_box['height'] * y_scale
    )

    page.mouse.up()


def checkbox_check_action(element: Locator, action: str = "check"):
    if action == "check":
        element.check()
    elif action == "uncheck":
        element.uncheck()
    else:
        print('only "check" and "uncheck" actions available')
