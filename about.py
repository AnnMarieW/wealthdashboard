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
plotly_logo = "https://user-images.githubusercontent.com/72614349/182969599-5ae4f531-ea01-4504-ac88-ee1c962c366d.png"
plotly_logo_dark = "https://user-images.githubusercontent.com/72614349/182967824-c73218d8-acbf-4aab-b1ad-7eb35669b781.png"
book_github = "https://github.com/DashBookProject/Plotly-Dash"
amw = "https://github.com/AnnMarieW"
adam = "https://www.youtube.com/c/CharmingData/featured"
chris = "https://finxter.com/"


def make_link(text, icon, link):
    return html.Span(html.A([html.I(className=icon + " ps-2"), text], href=link))


button = dbc.Button(
    "order", color="primary", href=nostarch, size="sm", className="mt-2 ms-1"
)

cover_img = html.A(
    dbc.CardImg(
        src=book_img,
        className="img-fluid rounded-start",
    ),
    href=nostarch,
)

text = dcc.Markdown(
    "Learn how to make this app in _The Book of Dash_ , a step-by-step"
    f" guide to making dashboards with Python, [Plotly and Dash.]({dash_url})",
    className="ps-2",
)

see_github = html.Span(
    [
        html.A([html.I(className=github + " p-1"), "GitHub"], href=book_github),
    ],
    className="lh-lg align-bottom",
)

authors = html.P(
    [
        "By ",
        make_link("Adam Schroeder ", youtube, adam),
        make_link("Christian Mayer", info, chris),
        make_link("Ann Marie Ward", github, amw),
    ],
    className="card-text p-2",
)

card = dbc.Card(
    [
        dbc.Row(
            [
                dbc.Col(cover_img, width=2),
                dbc.Col(
                    [text, button, see_github],
                    width=10,
                ),
            ],
            className="g-0 d-flex align-items-center",
        ),
        dbc.Row(dbc.Col(authors)),
    ],
    className="my-5 small shadow",
    style={"maxWidth": "32rem"},
)

app.layout = dbc.Container(card, fluid=True)

if __name__ == "__main__":
    app.run_server(debug=True)
