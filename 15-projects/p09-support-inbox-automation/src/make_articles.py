"""
make_articles.py - write 15 short help-centre articles (Markdown) for the fictional shop GadgetCo.

The workflow retrieves the best-matching article for each email and uses it in
the draft reply. Run:  python -m src.make_articles  -> data/help_articles/*.md
"""
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"

ARTICLES = {
    "refund-policy": ("Refunds and returns", "You can return any product within 30 days for a full refund. Start a return in "
                      "My Orders, print the free label, and the refund reaches your card 5-7 working days after we receive the item."),
    "delivery-times": ("Delivery times and tracking", "Standard delivery takes 3-5 working days. Track your parcel from the "
                       "link in your dispatch email. If tracking has not updated for 7 days, we open an investigation with the courier."),
    "damaged-items": ("Damaged or faulty items", "If your item arrives damaged, send a photo of the item and the box within 14 days. "
                      "We send a free replacement or a full refund, whichever you prefer."),
    "safety-issues": ("Product safety", "If a device smokes, sparks or gets very hot, unplug it immediately and stop using it. "
                      "Our safety team will contact you within 24 hours and arrange a collection."),
    "cancel-order": ("Cancelling an order", "Orders can be cancelled in My Orders until they are dispatched. After dispatch, "
                     "refuse the delivery or start a free return."),
    "double-charge": ("Charged twice or wrong amount", "A second charge is often a temporary card authorisation that disappears "
                      "within 3 working days. If it is still there after 3 days, reply with your bank statement line and we refund it."),
    "account-login": ("Can't log in", "Use Forgot password on the login page. Reset emails can take 10 minutes and may land in spam. "
                      "If your account is locked, our team can unlock it after verifying your identity."),
    "aquapure-setup": ("AquaPure Filter setup", "Rinse the cartridge for 5 minutes before first use and replace it every 3 months. "
                       "The blue light means the cartridge needs changing."),
    "smartkettle-setup": ("SmartKettle 2 app pairing", "Hold the power button for 5 seconds until the light flashes, then add the "
                          "kettle in the GadgetCo app. Use a 2.4 GHz Wi-Fi network; 5 GHz is not supported."),
    "fitband-pairing": ("FitBand Pro pairing", "Turn on Bluetooth, open the app and choose Add device. If pairing fails, restart "
                        "the band by holding the button for 10 seconds and try again."),
    "soundbuds-connect": ("SoundBuds X connection problems", "Put both buds in the case, hold the case button for 8 seconds to reset, "
                          "then pair again. Update the firmware in the app."),
    "homecam-wifi": ("HomeCam 360 keeps disconnecting", "Move the camera closer to the router, use 2.4 GHz Wi-Fi and update the "
                     "firmware. A weak signal is the most common cause of disconnections."),
    "warranty": ("Warranty", "All GadgetCo products have a 2-year warranty covering manufacturing faults. Keep your order number "
                 "as proof of purchase."),
    "feedback": ("Sharing feedback", "Thank you for your feedback! Reviews on our website help other customers and our product team."),
    "contact-us": ("Contacting support", "Our support team answers emails within 24 hours, Monday to Saturday. Urgent safety issues "
                   "are handled 7 days a week."),
}


def main():
    folder = DATA / "help_articles"
    folder.mkdir(parents=True, exist_ok=True)
    for slug, (title, body) in ARTICLES.items():
        (folder / f"{slug}.md").write_text(f"# {title}\n\n{body}\n", encoding="utf-8")
    print(f"wrote {len(ARTICLES)} articles -> data/help_articles/")


if __name__ == "__main__":
    main()
