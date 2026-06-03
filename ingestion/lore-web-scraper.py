import json

import requests
from bs4 import BeautifulSoup


def request_page(url) -> BeautifulSoup | None:
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.text, "html.parser")
    else:
        return None


if __name__ == "__main__":
    url = "https://www.windowscentral.com/resident-evil-story-so-far"
    soup = request_page(url)
    if not soup:
        print("Gagal mengambil halaman.")
        exit()

    hasil_akhir = []

    # Iterasi h2 sebagai anchor/judul
    for h2 in soup.select("#article-body h2"):
        title = h2.text.strip()
        p_data = []

        # Ambil semua sibling p sampai bertemu h2 berikutnya
        for sibling in h2.find_next_siblings():
            if sibling.name == "h2":
                break
            if sibling.name == "p":
                text_p = sibling.text.strip()
                if text_p:
                    p_data.append(text_p)

        if p_data:
            hasil_akhir.append({"title": title, "data": p_data})

    # MENYIMPAN KE FILE JSON
    file_name = "C:\Kuliah\Semester 8\Skripsi\Resident-Evil-Lore_LLM\Data\\resident_evil_story.json"
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(hasil_akhir, f, indent=4, ensure_ascii=False)

    print(f"Berhasil! Data telah disimpan di {file_name}")
