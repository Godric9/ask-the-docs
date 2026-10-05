# Corpus

Source : [DataDog/documentation](https://github.com/DataDog/documentation), commit pinné
`b2b73966dea62fbc39d49ee155c0bce4d3d85d81`.

Sous-dossier gardé : `hugo/content/en/getting_started` (64 fichiers `.md`, ~756K).

Licence du contenu (texte de la doc) non clairement permissive pour redistribution complète
(le `LICENSE` du repo couvre le code du site, pas explicitement le texte). Par précaution, le
contenu n'est pas commité ici — seule cette procédure de régénération l'est.

## Régénérer

```bash
git clone --filter=blob:none --sparse https://github.com/DataDog/documentation.git /tmp/dd-docs
cd /tmp/dd-docs
git checkout b2b73966dea62fbc39d49ee155c0bce4d3d85d81
git sparse-checkout set hugo/content/en/getting_started
cp -r hugo/content/en/getting_started/* /path/to/ask-the-docs/data/
rm -rf /tmp/dd-docs
```
