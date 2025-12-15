# English Learning Agent


## Lokalne uruchomienie

1. **Sklonuj repozytorium**

```bash
git clone <url>
```

2. **Utwórz nowy branch**

```bash
git checkout -b <nazwa_brancha>
```

3. **Stwórz środowisko wirtualne i zsynchronizuj zależności**

```bash
uv sync
```

4. **Stwórz plik .env i sprecyzuj w nim model oraz klucz API**

5. **Uruchom aplikację**

```bash
uv run python main.py
```

Aplikacja będzie znajodwała się pod poniższymi URL:

- http://127.0.0.1:8090/
- http://127.0.0.1:8090/docs

---

## Treść zadania

1. Dodaj historię konwersacji, pamiętając o kontroli jej długości. (5 pkt) (https://ai.pydantic.dev/message-history/)
2. Dodaj możliwość dodawania przez agenta fiszek (5 pkt). Wystarczy zapisywać w liście w pamięci RAM. (https://ai.pydantic.dev/tools/#registering-function-tools-via-decorator)
3. Obsłuż logikę iterowania po całej kolekcji fiszek (10 pkt).
4. Dodaj limit liczby wykonywanych requestów oraz procesówanych przez model tokenów. (5 pkt) (https://ai.pydantic.dev/agents/#usage-limits)
5. Dodatkowo: Zmodyfikuj logikę aplikacji aby jednocześnie mogła obsługiwać wielu użytkowników. (15 pkt)
