import numpy as np
import plotly.graph_objects as go
import plotly.io as pio

from pathlib import Path

from rosbags.rosbag2 import Reader
from rosbags.typesys import Stores, get_typestore

from artefacts_toolkit_utilities import extract_attribute_data

"""
Makes a chart based on provided topics (x, y) where each topic is a string with the format
"topic.attribute1.attribute2...". Attributes are split by "." Any depth of attributes can be used.
If one of the topics is time, the other topic will be plotted against its timestamps.
"""


def _make_rosbag_chart(filepath, topic_x, topic_y, field_unit, output_dir, chart_name):
    try:
        typestore = get_typestore(Stores.LATEST)
        x_data = []
        y_data = []
        initial_timestamp = None
        x_plot_name = f"{topic_x} ({field_unit})" if field_unit else topic_x
        y_plot_name = f"{topic_y} ({field_unit})" if field_unit else topic_y

        # Override plot names if one of the topics is time
        if topic_x.lower() == "time":
            x_plot_name = "Time (s)"
        if topic_y.lower() == "time":
            y_plot_name = "Time (s)"

        topic_x_attributes = topic_x.split(".")
        topic_y_attributes = topic_y.split(".")
        with Reader(filepath) as reader:
            for connection, timestamp, rawdata in reader.messages():
                msg = typestore.deserialize_cdr(rawdata, connection.msgtype)

                # Use the rosbag2 timestamp (epoch) if no header
                if not hasattr(msg, "header"):
                    msg_timestamp = timestamp / 1e9  # nanoseconds to seconds
                    if initial_timestamp is None:
                        initial_timestamp = msg_timestamp
                    normalized_timestamp = msg_timestamp - initial_timestamp
                else:
                    normalized_timestamp = (
                        msg.header.stamp.sec + msg.header.stamp.nanosec / 1e9
                    )

                # If only one actual topic is provided, use that topic's timestamps or rosbag time
                if (
                    topic_x.lower() == "time"
                    and connection.topic == topic_y_attributes[0]
                ):
                    x_data.append(normalized_timestamp)
                elif connection.topic == topic_x_attributes[0]:
                    x_data.append(extract_attribute_data(msg, topic_x_attributes))
                if (
                    topic_y.lower() == "time"
                    and connection.topic == topic_x_attributes[0]
                ):
                    y_data.append(normalized_timestamp)
                elif connection.topic == topic_y_attributes[0]:
                    y_data.append(extract_attribute_data(msg, topic_y_attributes))

        x_data = np.array(x_data)
        y_data = np.array(y_data)
        output_filepath = f"{output_dir}/{chart_name}.html"
        _plot_data(x_data, y_data, x_plot_name, y_plot_name, output_filepath)

    except Exception as e:
        print(f"ERROR: Unable to create chart for {chart_name}. {e}")


def _plot_data(x_data, y_data, x_title, y_title, output_filepath):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=x_data, y=y_data, mode="lines+markers", name=y_title))

    fig.update_layout(
        title=f"{y_title} vs {x_title}",
        xaxis_title=x_title,
        yaxis_title=y_title,
    )

    pio.write_html(fig, file=output_filepath, auto_open=False)


def make_chart(
    filepath,
    topic_x,
    topic_y,
    field_unit=None,
    output_dir="output",
    chart_name="chart",
    file_type="rosbag",
):
    try:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        for p in Path(output_dir).glob(f"{chart_name}.html"):
            p.unlink()
    except Exception as e:
        print(e)

    if file_type == "rosbag":
        _make_rosbag_chart(
            filepath, topic_x, topic_y, field_unit, output_dir, chart_name
        )
    else:
        raise NotImplementedError(
            "At present, charts can only be created from rosbags."
        )
