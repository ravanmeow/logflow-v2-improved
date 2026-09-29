# LogFlow — Artırım 1: İskelet Hat

Bir log dosyasını **hat (pipeline)** üzerinden okuyup konsola yazan küçük bir sistem.
Değer bu hafta görünmez; hattın esnekliği sonraki artırımlarda ortaya çıkar.

## Çalıştırma (Python 3.8+, ek paket yok)

    py main.py data/access-small.log          # Windows
    python3 main.py data/access-small.log     # macOS / Linux
    py main.py --help

## Testler

    py -m unittest discover -s tests -v

Testler; boş hat, filtre (0/1 çıktı), bölücü (N çıktı), stage sırası, `open/close`
yaşam döngüsü, hata durumunda `close`, CRLF satır sonu ve uçtan uca çıktıyı doğrular.

## Sözlük
| Terim | Anlamı | Bizde |
|---|---|---|
| Record | Hattan akan veri birimi | log satırı (`str`) |
| Stage | Kaydı işleyen, 0/1/N çıktı üretebilen bileşen | bu hafta yok |
| Source | Kayıt üretir | `FileLineSource` |
| Sink | Kayıt tüketir | `ConsoleSink` |
| Pipeline | Zinciri kurar ve çalıştırır | `Pipeline` |

## Dizin
    logflow/          emitter, stage, source, sink (arayüzler); file_line_source,
                      console_sink (uygulamalar); pipeline
    main.py           argüman oku → hattı kur → run()
    tests/            birim ve uçtan uca testler
    data/             access-small.log (200 satır)
    ARCHITECTURE.md   mimari açıklama

## Tasarım notu
`Stage.process` değer döndürmez, `Emitter` ile yayar: filtre 0, ayrıştırıcı N çıktı
üretebilir; dönüş değeri 1:1'e zorlar (bkz. `tests/test_pipeline.py`).

S�rüm: `v1`
