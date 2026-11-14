# Activate the BANG IPTV Stripe support page

The real Stripe Buy Button embed provided by the project creator is now installed in [docs/support/index.html](support/index.html). It includes the supplied public `buy-button-id` and `pk_live_` publishable key. **No secret key has been added.**

**The checkout page is not published yet:** GitHub Pages is disabled for this repository. A GitHub README cannot run JavaScript or a `<stripe-buy-button>` component.

## One-time GitHub Pages setup

1. Go to the repository's [Settings → Pages](https://github.com/sacuar/MyIPTV/settings/pages).
2. Under **Build and deployment**, choose **Deploy from a branch**.
3. Choose **Branch: main**, **Folder: /docs**, then **Save**.
4. Once GitHub confirms deployment, visit **https://sacuar.github.io/MyIPTV/support/** and verify the Stripe Buy Button renders.
5. In Stripe's dashboard, confirm the live payment description, currency, amount and payment methods are correct. Check the Stripe checkout page opens before sharing the link publicly. You do not need to make a payment to confirm the checkout form opens.

When that public support URL is live, edit [README.md](../README.md) and make the Stripe badge point to `https://sacuar.github.io/MyIPTV/support/` instead of this guide.

## Already have a public Payment Link?

If you prefer to avoid GitHub Pages altogether, copy the **public** `https://buy.stripe.com/...` link from [Stripe Payment Links](https://dashboard.stripe.com/payment_links). That URL can be used directly in GitHub Markdown and does not require a JavaScript embed or a separate website.

The embedded `buy_btn_...` identifier is **not** the same as a direct Payment Link URL; one cannot reliably be reconstructed from the other.

## Privacy and support

- The `pk_live_...` publishable key is designed to appear in publicly served web pages. Keep `sk_live_...` secret API keys out of this repository.
- The payment interface is hosted and processed by Stripe; don't collect or store payment-card data on GitHub.
- Buy Me a Coffee remains an independent option: https://buymeacoffee.com/sacuar
- Contributions are optional; BANG IPTV remains free to download and use under the applicable release terms.
