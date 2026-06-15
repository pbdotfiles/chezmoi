import os
import threading
from datetime import datetime

PLOT_DIR = "/tmp/ipython_plots"


def setup_spyder_gallery():
    os.makedirs(PLOT_DIR, exist_ok=True)

    # 1. Matplotlib Hook
    try:
        import matplotlib.pyplot as plt

        def custom_mpl_show(*args, **kwargs):
            timestamp = datetime.now().strftime("%H%M%S_%f")
            filename = f"{PLOT_DIR}/plot_{timestamp}.png"
            plt.savefig(filename, bbox_inches="tight", dpi=150)
            print(f"\n🖼️ Matplotlib saved to gallery: {filename}")
            plt.clf()
            plt.close("all")

        plt.show = custom_mpl_show
    except ImportError:
        pass

    # 2. Plotly Hook
    try:
        import plotly.io as pio

        def save_thumbnail_bg(fig, filename):
            """Background worker to save the Kaleido thumbnail."""
            try:
                fig.write_image(filename, width=900, height=600)
            except Exception:
                pass  # Silently fail if kaleido isn't installed or crashes

        def custom_plotly_show(fig, *args, **kwargs):
            timestamp = datetime.now().strftime("%H%M%S_%f")
            base_filename = f"{PLOT_DIR}/plot_{timestamp}"

            # Save the heavy interactive HTML immediately (fast)
            fig.write_html(f"{base_filename}.html")
            print(f"\n📈 Plotly saved to gallery: {base_filename}.html")

            # Fire and forget the Kaleido thumbnail generation in the background
            thumb_thread = threading.Thread(
                target=save_thumbnail_bg,
                args=(fig, f"{base_filename}.png"),
                daemon=True,  # Important: allows Python to exit even if this is still running
            )
            thumb_thread.start()

        pio.show = custom_plotly_show
    except ImportError:
        pass


setup_spyder_gallery()
