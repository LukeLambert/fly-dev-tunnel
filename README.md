# Fly Dev Tunnel

Developers commonly use apps like [ngrok](https://ngrok.com), [localtunnel](https://localtunnel.github.io/www/), or [cloudflared](https://github.com/cloudflare/cloudflared) to expose a local web service at a publicly-accessible URL. This is useful  for developing with HTTPS or sharing a site preview with a colleague or client.

By utilizing [Fly](https://fly.io), [WireGuard](https://www.wireguard.com), and a reverse proxy, you can achieve something similar with the added benefits of a custom domain and subdomains mapped to specific ports. Best of all, it’s free as long as you stay within Fly’s [generous limits](https://fly.io/docs/about/pricing/).

## 1. Install flyctl, the Fly command-line utility

[Follow the instructions](https://fly.io/docs/flyctl/installing/) for your OS. After installation, run `fly auth login` to sign up or sign in.

## 2. Connect to Fly via WireGuard

[Install WireGuard](https://www.wireguard.com/install/) for your OS. Next, run `fly wireguard create` to create a WireGuard config. Save it as `Fly.conf`. Make note of your region and peer IP address. You can also view them with `fly wireguard list`.

Note: The default config sets Fly as your DNS resolver. If you don’t need Fly’s internal DNS features, edit `Fly.conf` and comment out the DNS line with a pound sign (`#`).

Finally, setup the tunnel in WireGuard:
- On Mac or Windows, open the WireGuard app and click `Import Tunnel(s) from File`. Once imported, click `Activate` to connect.
- On Linux, [use the command line](https://fly.io/docs/reference/privatenetwork/#ubuntu-linux).

## 3. Create the reverse proxy app

Run `mkdir tunnel && cd tunnel` to create an empty app folder. Run `fly launch --image lukelambert/fly-dev-tunnel` to create the app. Give it a name and select the same region as your WireGuard connection from step 2.

## 4. Configure the reverse proxy

The reverse proxy is configured using two environment variables:

- `SUBDOMAINS`: A comma-separated list in the format `subdomain:local_port`. An underscore (`_`) matches the default (catch all) domain.
- `UPSTREAM`: The private IPv6 address of your local machine on the WireGuard network from step 2.

Edit `fly.toml` and update the `[env]` section with your values:

```
[env]
  SUBDOMAINS = "_:8000"
  UPSTREAM = "your-peer-ip"
```

## 5. Deploy the reverse proxy

Run `fly deploy`. Once the app is deployed, you should have a tunnel from `https://your-app-name.fly.dev` to port `8000` on your local machine.


## 6. (Optional) Connect custom (sub)domains

Visit the [Apps dashboard](https://fly.io/apps/) and select your app. Under the Certificates section, follow the instructions to add a custom domain. You can also add a wildcard subdomain, but this incurs a monthly fee. To map subdomains to local ports, update your `fly.toml` and re-run `fly deploy`. Example:

```
[env]
  SUBDOMAINS = "_:8000,app1:9001,app2:9002"
  UPSTREAM = "your-peer-ip"
```

## Notes

All traffic is proxied over IPv6, so your local web service should bind to an IPv6 address. To take down the tunnel and prevent traffic from reaching your machine, simply deactivate the WireGuard tunnel.
