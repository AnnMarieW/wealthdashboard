import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB, dbc.icons.FONT_AWESOME])

book_img = "https://user-images.githubusercontent.com/72614349/185497519-733bdfc3-5731-4419-9a68-44c1cad04a78.png"
nostarch = "https://nostarch.com/book-dash"
github = "fa-brands fa-github"
youtube = "fa-brands fa-youtube"
info = "fa-solid fa-circle-info"
plotly = "https://plotly.com/python/"
dash_url = "https://dash.plotly.com/"
book_github ="https://github.com/DashBookProject/Plotly-Dash/tree/master/Chapter-6"


card = dbc.Card(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.CardImg(
                        src=book_img,
                        className="img-fluid rounded-start",
                    ),
                    className="col-md-4",
                ),
                dbc.Col(
                    dbc.CardBody(
                        [
                            html.H4("Learn how to make this app!", className="card-title"),
                            dcc.Markdown(
                                f"This Asset Allocation Visualizer is featured in the The Book of Dash.  You too can make apps like this with "
                                 "[Plotly]({plotly}) and [Dash]({dash_url})",

                                className="card-text p-2",
                            ),

                           dbc.Button("Pre order your copy today!", color="primary", href=nostarch),

                            html.P([

                                html.I()

                                ],className="card-text",
                            ),
                        ]
                    ),
                    className="col-md-8",
                ),
            ],
            className="g-0 d-flex align-items-center",
        )
    ],
    className="mb-3",
    style={"maxWidth": "540px"},
)

app.layout= dbc.Container(
    [
        dbc.Row(dbc.Col(
            [
                card

            ]
        ))
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)