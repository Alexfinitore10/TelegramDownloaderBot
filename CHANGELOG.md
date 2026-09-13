# Changelog

## [0.2.4] - 2026-09-07
- **Aggiornamento yt-dlp**: Forzato l'aggiornamento all'ultima versione master di yt-dlp per risolvere i problemi di download con i link di YouTube (inclusi gli short link youtu.be).

## [0.2.3] - 2026-06-30
- **Fix Reel Instagram**: Risolto problema scaricamento Reel aggiornando yt-dlp al branch master e integrando il supporto all'impersonation con curl_cffi.
- **Supporto Foto Platform-Agnostic**: Implementato modo di scaricare foto da post (Instagram, Reddit, X, Facebook, ecc.) con invio automatico come immagine o carosello.
- **Fix Notifiche & Log Startup**: Risolto problema di parsing del changelog su Telegram (passaggio a parse_mode HTML per evitare errori di entità) e reso dinamico il log della versione all'avvio.

## [0.2.2] - 2026-06-19
- **Cap Qualità 1080p**: I video brevi (< 5 min) ora vengono scaricati a max 1080p anziché alla massima risoluzione disponibile (4K). Riduce drasticamente la dimensione dei file senza perdita di qualità percepibile.
- **Anti Rate-Limit YouTube**: Aggiunto delay di 3-6 secondi tra le richieste a YouTube per evitare blocchi temporanei.
- **Fasce Qualità Semplificate**: Video < 5 min → 1080p, 5-15 min → 720p, ≥ 15 min → 720p.

## [0.2.1] - 2026-06-17
- **Bypass TikTok**: Implementato meccanismo di fallback nei download di tiktok con cookie (risolto errore login required).

## [0.2.0] - 2026-06-15
- **Countdown Deltarune**: Aggiunto countdown automatico che ogni notte alle 00 informa sui giorni mancanti al 24 giugno.
- **Qualità Video Ottimizzata**: Migliorata la qualità dei download. I video brevi sono ora scaricati alla massima risoluzione disponibile, con degradazione intelligente per video molto lunghi per ottimizzare i tempi e lo spazio.
- **Logging Silenzioso**: Ridotto drasticamente il log bloat. Ora vengono registrati solo Errori e Warning, mantenendo il sistema più pulito e leggero.

## [0.1.1] - 2026-06-09
- **Supporto Playlist/Multi-video**: Ora il bot scarica correttamente tutti i video presenti in un singolo link (es. post di X con più media).
- **Notifiche Aggiornamento**: Il bot comunicherà automaticamente le novità in chat ad ogni nuovo rilascio.
- **Feedback Migliorato**: Aggiunte notifiche specifiche quando un link contiene solo foto o contenuti non supportati (es. post Facebook di sole immagini).
