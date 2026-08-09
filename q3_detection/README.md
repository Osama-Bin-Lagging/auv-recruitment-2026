# Q3: Gate Detection

Optional, and scored separately from Q1 and Q2. It's here to find people for the
vision subsystem. Skipping it costs you nothing.

## The data

Real footage from our pool, of the competition gate signs. Those are the red and
blue symbols the vehicle reads to work out which side of a gate to pass through.

In `release/`:

| split | images |
|---|---|
| train | 2,329 |
| valid | 292 |

Two classes, `blue_side` and `red_side`. Labels are YOLO format.

## The task

Train a detector, then give us an inference script matching this exactly:

```bash
python infer.py --input <image_dir> --output predictions.json
```

One entry per image:

```json
{
  "frame_0001.jpg": [
    {"class": "blue_side", "confidence": 0.91, "bbox": [x, y, w, h]},
    {"class": "red_side",  "confidence": 0.87, "bbox": [x, y, w, h]}
  ]
}
```

`bbox` in pixels, `[x, y, w, h]`, top-left origin.

## Constraints

CPU only, 100 ms per frame averaged over the set. An AUV has no GPU, and a gate
you recognise at 2 fps is a gate you've already hit. Over budget doesn't get
scored.

Ship your weights.

## Grading

mAP@0.5 on a held-out test set, from footage that isn't in your download.

Something to know before you start. The training data comes from two recording
sessions in two different pools, and they look nothing alike. One is shallow and
green with the signs close and large. The other is a deep blue competition pool
where the signs are small and distant. The median object is about 3.5 times
smaller in one than the other.

A default fine-tune at default settings handles one of those and not the other.
That's the actual problem. Look at your data before you trust anything your
training script prints.

## Submitting

`infer.py`, your weights, and a pinned `requirements.txt`.

Write up this question in `REPORT.md` at the root of your fork. See the
[submission instructions](../README.md#the-report).
