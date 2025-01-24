from typing import Any, TypeAlias


Configuration: TypeAlias = dict[str, Any]


def basic_animation_configuration(redraw: bool = False) -> Configuration:
    return dict(
        type="buttons",
        buttons=[
            play_button(redraw),
            pause_button(redraw),
            restart_button(redraw),
        ],
    )


def play_button(redraw: bool = True) -> Configuration:
    return dict(
        label="Play",
        method="animate",
        args=[
            None,
            {
                "frame": {"duration": 10, "redraw": redraw},
                "fromcurrent": True,
                "transition": {"duration": 0},
            },
        ],
    )


def pause_button(redraw: bool = True) -> Configuration:
    return dict(
        label="Pause",
        method="animate",
        args=[
            [None],
            {
                "frame": {"duration": 0, "redraw": redraw},
                "mode": "immediate",
                "transition": {"duration": 0},
            },
        ],
    )


def restart_button(redraw: bool = True) -> Configuration:
    return dict(
        label="Restart",
        method="animate",
        args=[
            None,
            {
                "frame": {"duration": 0, "redraw": redraw},
                "fromcurrent": False,
                "transition": {"duration": 0},
            },
        ],
    )
