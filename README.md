# Web Proxy Scraper/Generator

A simple, colorful, terminal-based tool to:
- Search for fresh proxy list links using Google (with custom queries)
- Scrape proxies from those links
- Test proxies for HTTP, SOCKS4, and SOCKS5 support

Uses [rich](https://github.com/Textualize/rich) for a semi-GUI experience and colored output.

---

## Features

- Multi-threaded for fast scraping and testing
- Supports HTTP, SOCKS4, SOCKS5 proxies
- Easy-to-use interactive menu
- Keyboard interrupt support (Ctrl+C to stop and return to menu)
- Output files: `links.txt`, `proxies.txt`, `working_proxies.txt`

---

## Requirements

- Python 3.8+
- [requests[socks]](https://pypi.org/project/requests/)  
- [rich](https://pypi.org/project/rich/)
- [googlesearch-python](https://pypi.org/project/googlesearch-python/)

Install all dependencies:
```
pip install requests[socks] rich googlesearch-python
```

---

## Usage

1. **Clone the repository:**
    ```
    git clone https://github.com/umar-devc/Web-Proxy-Scrapper.git
    cd Web-Proxy-Scrapper
    ```

2. **Prepare your search queries:**
    - Edit `query.txt` and add one search query per line (examples included).

3. **Run the script:**
    ```
    python proxy.py
    ```

4. **Follow the menu:**
    - **1:** Web search and extract links for proxies (uses your queries in `query.txt`)
    - **2:** Scrape proxies from links (from `links.txt` or your chosen file)
    - **3:** Test proxies from file (default: `proxies.txt`)
    - **q:** Quit

    You will be prompted for number of workers (threads) for each operation.

---

## Example Workflow

1. Add queries to `query.txt` (e.g., `fresh proxy filetype:txt site:github.com`)
2. Run the script and choose option 1 to search and save links.
3. Choose option 2 to scrape proxies from those links.
4. Choose option 3 to test the scraped proxies.

---

## Notes

- For SOCKS proxy support, `requests[socks]` and `PySocks` must be installed.
- If you get errors about `googlesearch`, install it with `pip install googlesearch-python`.
- All output and prompts are colored and menu is centered for a better terminal experience.

---

## License

MIT License

---

**Enjoy fast, easy proxy scraping and testing!**