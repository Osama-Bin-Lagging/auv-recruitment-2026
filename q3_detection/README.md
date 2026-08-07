# Q3 — Gate Detection *(optional)*

**Computer vision · ~4 hours · only if Q1 and Q2 are done**

This one is optional and scored separately. It exists to find people for the
vision subsystem, not to rank everyone. Skipping it costs you nothing.

## The data

Real footage from our pool, of the competition gate signs — the same red and
blue symbols the vehicle has to recognise to know which side of a gate to pass
through.

Download the dataset from the repo's Releases page.

| split | images |
|---|---|
| train | 2,329 |
| valid | 292 |

Two classes: `blue_side`, `red_side`. Labels are YOLO format.

## The task

Train a detector, then submit an inference script matching this contract
exactly:

```bash
python infer.py --input <image_dir> --output predictions.json
```

`predictions.json` — one entry per image:

```json
{
  "frame_0001.jpg": [
    {"class": "blue_side", "confidence": 0.91, "bbox": [x, y, w, h]},
    {"class": "red_side",  "confidence": 0.87, "bbox": [x, y, w, h]}
  ]
}
```

`bbox` is pixels, `[x, y, w, h]`, top-left origin.

## Constraints

- **CPU only, 100 ms per frame average.** An AUV has no GPU and a gate you
  recognise at 2 fps is a gate you have already hit. Over budget is not scored.
- Ship your weights with the submission.

## How it's graded

mAP@0.5 on a **held-out test set you have never seen**, drawn from footage that
is not in your download.

Worth knowing before you start: the training data comes from **two different
recording sessions in two different pools**, and they look nothing alike — one
is shallow and green with the signs close and large, the other is a deep blue
competition pool where the signs are small and far away. The median object is
roughly **3.5× smaller** in one than the other.

A default fine-tune at default settings handles one of those and not the other.
That is the actual problem here, and it is worth looking at your data before you
trust any number your training script prints.

## Submit

`infer.py`, your weights, a `requirements.txt` that pins what you used, and
half a page on your augmentation strategy and why.
