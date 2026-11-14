# Set up an optional Stripe support button

BANG IPTV's README already displays an **unlinked Stripe icon** with the label **Link not added yet**. It intentionally does not send visitors to an unverified payment destination.

## Add your public Stripe Payment Link

1. Log in to your own [Stripe Dashboard](https://dashboard.stripe.com/payment_links) and create or select a suitable public Payment Link for optional project support.
2. Copy the **public HTTPS Payment Link** (normally a URL starting `https://buy.stripe.com/`). Never copy an API secret key, restricted API key, live checkout-session URL or a Stripe dashboard URL.
3. Open [README.md](../README.md), choose **Edit**, and find the **Support the creator** table.
4. Replace the existing *non-clickable* Stripe image with a linked badge, substituting your actual verified public URL:

   ```markdown
   [![Support via Stripe](https://img.shields.io/badge/Stripe-Support_the_creator-635BFF?logo=stripe&logoColor=white)](https://buy.stripe.com/YOUR_PUBLIC_PAYMENT_LINK)
   ```

5. Replace the explanatory placeholder below it with a short message, e.g. `Optional, secure card payment through Stripe`. Preview the README and commit.

**Do not treat this project as a registered charity or use charitable tax-relief claims unless that status has been established.** An optional contribution may be a taxable business receipt; seek professional accounting advice as appropriate.

For a seamless handoff, send the exact public Stripe Payment Link and the repository can be updated without touching application source or releases.
