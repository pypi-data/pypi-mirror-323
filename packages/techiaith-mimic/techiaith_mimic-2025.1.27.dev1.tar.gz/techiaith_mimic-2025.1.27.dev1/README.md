# MIMiC - Modelau Iaith Mawr i'r Cymraeg

## Cychwyn arni

Gosod amgylchedd Python yn defnyddio [mamba](https://storfa.techiaith.cymru/gweinyddion/gosodiad-datblygwr#setup-conda-with-mamba):

```bash
git clone https://storfa.techiaith.cymru/projectau-techiaith/iriaith/cyfieithu-ac-llms/hyfforddi/mimic.git
cd mimic
mamba create -n mimic
mamba env update --file config/local-env.yaml
make build
```

## Defnyddio

```bash
docker compose up -d --remove-orphanx
```

### Rhedeg biblinell DVC

```bash
dvc exp run
```

### TODO

Dyma rhestr o pethau efallai eisiau newid i'w rhedeg eich hunnain:

- Newid GPUs yn yr ffeil `docker-compose.yaml`.
- Yr model i'w hyfforddi yn `base_model` mewn nodyn `vars` o fewn yr ffeil `dvc.yaml`.
- Newid parameredau hyfforddi `autotrain` o fewn ffeil `params.yaml`.

### Rhedeg inference yn erbyn unrhyw model

```bash
docker compose exec mimic accelerate launch -m techiaith.mimic.inference --help
```
