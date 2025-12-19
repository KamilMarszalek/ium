import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import FuncFormatter, MultipleLocator

DISCRETE_COLUMNS = {
    "accommodates",
    "bedrooms",
    "beds",
}

LOGY_COLUMNS = {
    "number_of_reviews",
    "minimum_nights",
    "maximum_nights",
}

NIGHTS_RANGES = {
    "maximum_nights",
    "minimum_nights",
}


def price_to_float(series: pd.Series) -> pd.Series:
    s = series.astype("string")
    s = s.str.replace(r"[^\d\.\-]", "", regex=True)
    return pd.to_numeric(s, errors="coerce")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def save_hist(
    series: pd.Series,
    title: str,
    xlabel: str,
    out_png: Path,
    pdf: PdfPages | None = None,
    bins: int | str | None = None,
    *,
    discrete: bool = False,
    clip_q: float | None = None,
    logx: bool = False,
    xtick_step: int | None = None,
    logy: bool = False,
) -> None:
    raw = pd.to_numeric(series, errors="coerce")
    missing = int(raw.isna().sum())
    s = raw.dropna()
    if s.empty:
        print(f"{title}: no data")
        return
    if clip_q is not None:
        hi = float(s.quantile(clip_q))
        s = s[s <= hi]
        fig, ax = plt.subplots(figsize=(9, 4.8), constrained_layout=True)
    fig, ax = plt.subplots(figsize=(9, 4.8), constrained_layout=True)
    if logx:
        s = s[s > 0]
        bins = np.logspace(np.log10(s.min()), np.log10(s.max()), 50)
        ax.hist(s, bins=bins)
        ax.set_xscale("log")
        ticks = [1, 2, 3, 5, 7, 10, 14, 30, 60, 90, 180, 365, 1000]
        ticks = [t for t in ticks if s.min() <= t <= s.max()]
        ax.set_xticks(ticks)
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x)}"))
        ax.axvline(14, linestyle="--")
        ax.text(
            14,
            0.95,
            "14",
            transform=ax.get_xaxis_transform(),
            ha="center",
            va="top",
        )

    elif discrete:
        lo = int(np.floor(s.min()))
        hi = int(np.ceil(s.max()))
        bins = np.arange(lo - 0.5, hi + 1.5, 1)
        ax.hist(s, bins=bins)
        ax.set_xlim(lo - 0.5, hi + 0.5)
        ax.xaxis.set_major_locator(
            MultipleLocator(1 if xtick_step is None else xtick_step)
        )
    else:
        ax.hist(s, bins=("auto" if bins is None else bins))

    if logy:
        ax.set_yscale("log")

    ax.set_title(title)
    ax.set_xlabel(xlabel + (" (skala log)" if logx else ""))
    ax.set_ylabel("Liczność")
    ax.grid(True, axis="y", alpha=0.3)
    ax.text(
        0.99,
        0.95,
        f"N={len(s)}  missing={missing}",
        transform=ax.transAxes,
        ha="right",
        va="top",
    )
    fig.savefig(out_png, dpi=200, bbox_inches="tight")
    if pdf is not None:
        pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def save_bar(
    series: pd.Series,
    title: str,
    xlabel: str,
    out_png: Path,
    pdf: PdfPages | None = None,
    fig_width: float = 12,
) -> None:
    counts = series.value_counts().sort_index()
    if counts.empty:
        print(f"{title}: no data")
        return

    fig, ax = plt.subplots(figsize=(fig_width, 5), constrained_layout=True)
    counts.plot(kind="bar", ax=ax)

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Liczność")
    ax.grid(True, axis="y", alpha=0.3)
    plt.xticks(rotation=45, ha="right")

    fig.savefig(out_png, dpi=200, bbox_inches="tight")
    if pdf is not None:
        pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def load_sessions(path: Path) -> pd.DataFrame:
    return pd.read_csv(
        path,
        dtype={
            "action": "string",
            "user_id": "string",
            "listing_id": "string",
            "booking_id": "string",
        },
    )


def build_bookings_from_sessions(sessions: pd.DataFrame) -> pd.DataFrame:
    book = sessions[sessions["action"] == "book_listing"].copy()
    book["checkin"] = pd.to_datetime(book.get("booking_date"), errors="coerce")
    book["checkout"] = pd.to_datetime(
        book.get("booking_duration"),
        errors="coerce",
    )
    book["booking_ts"] = pd.to_datetime(book.get("timestamp"), errors="coerce")

    book["nights"] = (book["checkout"] - book["checkin"]).dt.days
    book = book[book["nights"].notna()]
    book = book[(book["nights"] > 0) & (book["nights"] <= 365)]

    if "booking_ts" in book.columns:
        book["lead_time_days"] = (book["checkin"] - book["booking_ts"]).dt.days
    book["long_stay"] = book["nights"] >= 7
    book["checkin_quarter"] = book["checkin"].dt.to_period("Q").astype("string")
    book["checkin_month"] = book["checkin"].dt.month

    return book


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", type=Path, default=Path("data"))
    ap.add_argument("--out-dir", type=Path, default=Path("plots"))
    ap.add_argument("--bins", type=int, default=None)
    args = ap.parse_args()

    data_dir: Path = args.data_dir
    out_dir: Path = args.out_dir
    ensure_dir(out_dir)

    sessions_path = data_dir / "sessions_repaired.csv"
    listings_path = data_dir / "listings_repaired.csv"
    reviews_path = data_dir / "reviews.csv"

    sessions = load_sessions(sessions_path)
    bookings = build_bookings_from_sessions(sessions)
    pdf_path = out_dir / "histograms.pdf"
    with PdfPages(pdf_path) as pdf:
        save_hist(
            bookings["nights"],
            title="Rozkład długości pobytu (nights)",
            xlabel="Liczba nocy",
            out_png=out_dir / "bookings_nights.png",
            pdf=pdf,
            bins=args.bins,
            discrete=True,
            xtick_step=1,
        )
        save_bar(
            bookings["checkin_quarter"],
            title="Rozkład kwartałów zameldowania",
            xlabel="Kwartał zameldowania",
            out_png=out_dir / "bookings_checkin_quarter.png",
            pdf=pdf,
        )

        if "lead_time_days" in bookings.columns:
            save_hist(
                bookings["lead_time_days"],
                title="Rozkład liczby dni wyprzedzenia rezerwacji dla book_listing",
                xlabel="Liczba dni wyprzedzenia rezerwacji",
                out_png=out_dir / "bookings_lead_time_days.png",
                pdf=pdf,
                bins=args.bins,
            )
        if listings_path.exists():
            listings = pd.read_csv(listings_path, dtype={"id": "string"})
            if "price" in listings.columns:
                price = price_to_float(listings["price"])
                save_hist(
                    price,
                    title="Rozkład ceny oferty (price) w listings.csv",
                    xlabel="Cena",
                    out_png=out_dir / "listings_price.png",
                    pdf=pdf,
                    logy=True,
                    bins=args.bins,
                )
                save_hist(
                    (price + 1).apply(
                        lambda x: None if pd.isna(x) else __import__("math").log10(x)
                    ),
                    title="Rozkład log10(price + 1) w listings.csv",
                    xlabel="log10(price + 1)",
                    out_png=out_dir / "listings_price_log10.png",
                    pdf=pdf,
                    bins=args.bins,
                )
            if "last_scraped" in listings.columns:
                save_bar(
                    pd.to_datetime(listings["last_scraped"], errors="coerce")
                    .dt.to_period("Q")
                    .astype("string"),
                    title="Rozkład kwartałów last_scraped w listings.csv",
                    xlabel="Kwartał ostatniego skrobania",
                    out_png=out_dir / "listings_last_scraped.png",
                    pdf=pdf,
                    fig_width=5,
                )

            for col in [
                "accommodates",
                "bedrooms",
                "beds",
                "bathrooms",
                "minimum_nights",
                "maximum_nights",
                "number_of_reviews",
            ]:
                if col in listings.columns:
                    save_kwargs = {}
                    if col in DISCRETE_COLUMNS:
                        save_kwargs["discrete"] = True
                        save_kwargs["xtick_step"] = 1
                    if col in LOGY_COLUMNS:
                        save_kwargs["logy"] = True
                    if col in NIGHTS_RANGES:
                        save_kwargs["discrete"] = True
                        save_kwargs["logx"] = True
                    save_hist(
                        listings[col],
                        title=f"Rozkład {col} w listings.csv",
                        xlabel=col,
                        out_png=out_dir / f"listings_{col}.png",
                        pdf=pdf,
                        bins=args.bins,
                        **save_kwargs,
                    )

        if reviews_path.exists():
            reviews = pd.read_csv(
                reviews_path,
                dtype={"listing_id": "string", "reviewer_id": "string"},
            )
            if "comments" in reviews.columns:
                comment_len = reviews["comments"].astype("string").str.len()
                save_hist(
                    comment_len,
                    title="Rozkład długości komentarza w reviews.csv",
                    xlabel="Długość komentarza (liczba znaków)",
                    out_png=out_dir / "reviews_comment_length.png",
                    pdf=pdf,
                    bins=args.bins,
                )
        plt.pie(
            bookings["long_stay"].value_counts(),
            labels=["Short stay", "Long stay"],
            autopct="%1.1f%%",
        )
        plt.title("Procent rezerwacji długoterminowych (long_stay)")
        pie_path = out_dir / "bookings_long_stay_pie.png"
        plt.savefig(pie_path, dpi=200, bbox_inches="tight")
        pdf.savefig(bbox_inches="tight")
        plt.close()

    print(f"saved PNGs + {pdf_path}")


if __name__ == "__main__":
    main()
