import re
import requests
import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import socks  # Needed for SOCKS proxies 
from rich.console import Console
from rich.prompt import Prompt
from rich.progress import track
from rich.panel import Panel
from rich.align import Align

try:
    from googlesearch import search
except ImportError:
    search = None

PROXY_TYPES = ["http", "socks4", "socks5"]
console = Console()

def get_links(filename):
    """Read all links from the given file and return as a list."""
    with open(filename, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def get_querylist(filename="query.txt"):
    """Retrieve all search keywords from the query.txt file as a list."""
    with open(filename, 'r', encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]

def web_search(query, num_results):
    """Perform a web search using the provided query and saves the links."""
    links = []
    console.print(f"[cyan]Searching for:[/cyan] {query}")
    try:
        for idx, url in enumerate(search(query, num_results=num_results), 1):
            links.append(url)
            console.print(f"[green][{idx}/{num_results}] {url}[/green]")
            time.sleep(random.uniform(1, 2))
    except Exception as e:
        console.print(f"[red]An error occurred during the search: {e}[/red]")
    finally:
        console.print(f"[cyan]Search completed. Found {len(links)} links.[/cyan]")
        with open("links.txt", "a", encoding="utf-8") as f:
            for link in links:
                f.write(link + "\n")

def scrape_proxies_from_link(link):
    """Extract proxy/ip addresses from links."""
    proxy_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}:\d{2,5}\b"
    proxies = set()
    try:
        console.print(f"[blue]Fetching:[/blue] {link}")
        res = requests.get(link, timeout=3)
        if res.status_code == 200:
            found = re.findall(proxy_pattern, res.text)
            proxies.update(found)
            console.print(f"[green]Found {len(found)} proxies.[/green]")
        else:
            console.print(f"[red]Failed to fetch {link} (status code: {res.status_code})[/red]")
    except Exception as e:
        console.print(f"[red]Error fetching {link}: {e}[/red]")
    return proxies

def check_proxy(proxy, proxy_types, lock):
    ip, port = proxy.split(":")
    worked = False
    for proxy_type in proxy_types:
        proxy_url = f"{proxy_type}://{ip}:{port}"
        proxies = {"http": proxy_url, "https": proxy_url}
        try:
            resp = requests.get("https://ipwho.is/", proxies=proxies, timeout=3)
            if resp.status_code == 200:
                console.print(f"[bold green][+] {proxy} ({proxy_type}) WORKING[/bold green]")
                with lock:
                    with open("working_proxies.txt", "a") as f:
                        f.write(f"{proxy} ({proxy_type})\n")
                worked = True
                break
            else:
                console.print(f"[red][-] {proxy} ({proxy_type}) NOT WORKING[/red]")
        except Exception:
            console.print(f"[red][-] {proxy} ({proxy_type}) NOT WORKING[/red]")
    return worked

def test_proxies(proxy_file, proxy_types, max_workers):
    """Test proxies from a file, try all types."""
    with open(proxy_file, "r", encoding="utf-8") as f:
        proxies = set(line.strip() for line in f if line.strip())
    console.print(f"[cyan]Testing {len(proxies)} proxies with {max_workers} workers...[/cyan]")
    lock = threading.Lock()
    working = set()
    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(check_proxy, proxy, proxy_types, lock): proxy for proxy in proxies}
            for future in as_completed(futures):
                proxy = futures[future]
                if future.result():
                    working.add(proxy)
    except KeyboardInterrupt:
        console.print("[yellow]Interrupted by user. Progress saved. Returning to menu...[/yellow]")
    console.print(f"\n[bold green]Total working proxies: {len(working)} (saved to working_proxies.txt)[/bold green]")

def main():
    while True:
        try:
            console.clear()
            console.rule("[bold cyan]Web Proxy Scraper/Generator[/bold cyan]", style="bold cyan")
            menu_text = (
                "[bold cyan]Options[/bold cyan]\n\n"
                "[bold yellow]1.[/bold yellow] Web search and extract links for proxies\n"
                "[bold yellow]2.[/bold yellow] Scrape proxies from links\n"
                "[bold yellow]3.[/bold yellow] Test proxies from file\n"
                "[bold yellow]q.[/bold yellow] Quit"
            )
            panel = Panel(
                Align.center(menu_text, vertical="middle"),
                style="on black",
                padding=(1, 8),
                width=60
            )
            console.print(panel, justify="center")
            choice = Prompt.ask("[bold yellow]Enter 1, 2, 3, or q[/bold yellow]").strip().lower()
            if choice == "1":
                if search is None:
                    console.print("[red]googlesearch module not found. Please install it to use this feature.[/red]")
                else:
                    queries = get_querylist()
                    if queries:
                        try:
                            num_results = int(Prompt.ask("[cyan]Enter Number Of Results Needed[/cyan]", default="10"))
                        except ValueError:
                            num_results = 10
                        try:
                            max_workers = int(Prompt.ask("[cyan]Number of workers?[/cyan]", default="5"))
                        except ValueError:
                            max_workers = 5

                        def search_task(query):
                            try:
                                web_search(query, num_results)
                            except Exception as e:
                                console.print(f"[red]Error searching for '{query}': {e}[/red]")

                        try:
                            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                                list(track(executor.map(search_task, queries), total=len(queries), description="Searching..."))
                        except KeyboardInterrupt:
                            console.print("[yellow]Interrupted by user. Returning to menu...[/yellow]")
                    else:
                        console.print("[red]No queries found in query.txt. Please input a search query in query.txt file.[/red]")
            elif choice == "2":
                links_file = Prompt.ask("[cyan]Enter the name of the links file[/cyan]", default="links.txt")
                output_file = Prompt.ask("[cyan]Enter the name of the output file[/cyan]", default="proxies.txt")
                try:
                    max_workers = int(Prompt.ask("[cyan]Number of workers?[/cyan]", default="20"))
                except ValueError:
                    max_workers = 20
                links = get_links(links_file)
                all_proxies = set()
                console.print(f"[cyan]Scraping proxies from {len(links)} links with {max_workers} workers...[/cyan]")
                def scrape_and_collect(link):
                    return scrape_proxies_from_link(link)
                try:
                    with ThreadPoolExecutor(max_workers=max_workers) as executor:
                        futures = {executor.submit(scrape_and_collect, link): link for link in links}
                        for idx, future in enumerate(track(as_completed(futures), total=len(links), description="Scraping..."), 1):
                            proxies = future.result()
                            all_proxies.update(proxies)
                            console.print(f"[green][{idx}/{len(links)}] Processed {futures[future]}[/green]")
                except KeyboardInterrupt:
                    console.print("[yellow]Interrupted by user. Progress saved. Returning to menu...[/yellow]")
                console.print(f"[bold green]Total unique proxies found: {len(all_proxies)}[/bold green]")
                with open(output_file, "w", encoding="utf-8") as f:
                    for proxy in all_proxies:
                        f.write(proxy + "\n")
            elif choice == "3":
                proxy_file = Prompt.ask("[cyan]Enter the proxy file to test[/cyan]", default="proxies.txt")
                proxy_type_input = Prompt.ask("[cyan]Proxy type? (http/socks4/socks5/all)[/cyan]", default="all").lower()
                try:
                    max_workers = int(Prompt.ask("[cyan]Number of workers?[/cyan]", default="50"))
                except ValueError:
                    max_workers = 50
                if proxy_type_input == "all":
                    proxy_types = PROXY_TYPES
                else:
                    proxy_types = [proxy_type_input]
                test_proxies(proxy_file, proxy_types, max_workers)
            elif choice == "q":
                console.print("[bold magenta]Goodbye![/bold magenta]")
                break
            else:
                console.print("[red]Invalid choice.[/red]")
        except KeyboardInterrupt:
            console.print("[yellow]Interrupted by user. Returning to menu...[/yellow]")
            continue

if __name__ == "__main__":
    main()