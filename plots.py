
import plotly.express as px
import plotly.io as pio
#
def plot(graph_title, accuracy_res):
    portions = [0.1, 0.5, 1]
    fig = px.line(x=portions, y=accuracy_res, title=graph_title)
    fig.update_layout(xaxis_title="portion", yaxis_title="accuracy",
                      xaxis=dict(tickvals=list(portions), tickmode='array'))
    pio.write_image(fig, f'{graph_title}.png')
    fig.show()



if __name__ == "__main__":
    portions = [0.1, 0.5, 1.]
    Logistic_regression_results = [0.7261273209549072, 0.8090185676392573, 0.8262599469496021]

    plot(f"Logistic regression accuracy", Logistic_regression_results)
    transformer_acc = [0.8183023872679045, 0.8985411140583555, 0.903183023872679]

    plot(f"Finetuning accuracy", transformer_acc)