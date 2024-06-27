import gradio as gr
import pandas as pd

# Sample data for the table
data = {
    "Item": ["Item 1", "Item 2", "Item 3"],
    "Description": ["Description 1", "Description 2", "Description 3"],
}
df = pd.DataFrame(data)


def show_details(index):
    selected_item = df.iloc[index]
    details = (
        f"Item: {selected_item['Item']}\nDescription: {selected_item['Description']}"
    )
    return details


def toggle_visibility(is_detail_visible):
    return not is_detail_visible


with gr.Blocks() as demo:
    # State for managing the visibility of the detail screen
    is_detail_visible = gr.State(value=False)
    selected_index = gr.State(value=None)

    with gr.Row(visible=not is_detail_visible.value) as initial_screen:
        gr.Markdown("# Select an Item from the Table")
        table = gr.Dataframe(value=df, interactive=True)

        def on_select(evt):
            return (evt.index[0], True)

        table.select(
            on_select, inputs=table, outputs=[selected_index, is_detail_visible]
        )

    with gr.Row(visible=is_detail_visible.value) as detail_screen:
        gr.Markdown("# Item Details")
        details = gr.Textbox(label="Details", interactive=False)
        back_button = gr.Button("Back")

        # Display details when an item is selected
        selected_index.change(show_details, inputs=selected_index, outputs=details)

        # Toggle visibility back to initial screen
        back_button.click(lambda: False, outputs=is_detail_visible)

    def on_detail_visibility_change(detail_visible):
        print("changed")
        return [
            gr.update(visible=not detail_visible),
            gr.update(visible=detail_visible),
        ]

    is_detail_visible.change(
        on_detail_visibility_change,
        inputs=is_detail_visible,
        outputs=[initial_screen, detail_screen],
    )
demo.launch()
