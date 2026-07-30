# Тестовое задание Python / Data Engineering

Автор решения: **Долгов Евгений**.

Репозиторий содержит воспроизводимое решение двух задач: анализ и изменение CVAT XML, а также реструктуризацию, проверку и конвертацию COCO-датасета в YOLO. Используется только стандартная библиотека Python — установка зависимостей не требуется.

## Структура

```text
.
├── task1/
│   ├── input/                    # три исходных XML
│   ├── output/
│   │   ├── *.json               # рассчитанная статистика
│   │   └── modified/             # XML после преобразования
│   ├── general_statistics.py
│   ├── class_statistics.py
│   ├── shape_statistics.py       # дополнительная часть
│   └── modify_annotations.py
├── task2/
│   ├── input/task_train_coco.zip # исходный COCO-датасет
│   ├── output/
│   │   ├── restructured_dataset/
│   │   ├── dataset_report.json
│   │   └── yolo_dataset/         # дополнительная часть
│   ├── restructure_coco.py
│   ├── validate_dataset.py
│   └── coco_to_yolo.py
└── tests/test_solution.py
```

## Требования

- Python 3.9 или новее;
- около 30 МБ свободного места при повторной генерации результатов.

Команды ниже выполняются из корня репозитория. В PowerShell вместо `python` при необходимости используйте `py`.

## Задача 1 — CVAT XML

Общая статистика:

```powershell
python task1/general_statistics.py task1/input/annotations.xml task1/input/annotations-2.xml task1/input/annotations-3.xml --output task1/output/general_statistics.json
```

Статистика классов и типов фигур:

```powershell
python task1/class_statistics.py task1/input/annotations.xml task1/input/annotations-2.xml task1/input/annotations-3.xml --output task1/output/class_statistics.json
python task1/shape_statistics.py task1/input/annotations.xml task1/input/annotations-2.xml task1/input/annotations-3.xml --output task1/output/shape_statistics.json
```

Разворот ID и нормализация имён:

```powershell
python task1/modify_annotations.py task1/input/annotations.xml task1/input/annotations-2.xml task1/input/annotations-3.xml --output-dir task1/output/modified
```

Скрипт разворачивает фактически встреченный список ID, поэтому корректно работает и с нестандартным порядком или непоследовательными значениями. В имени остаётся только basename, расширение заменяется на `.png`. Исходные файлы не перезаписываются.

## Задача 2 — COCO

Сначала распакуйте `task2/input/task_train_coco.zip` в произвольную папку, например `work/coco_source`.

Реструктуризация с перемещением изображений (как указано в задании):

```powershell
python task2/restructure_coco.py work/coco_source/annotations/instances_train.json work/coco_source/images task2/output/restructured_dataset
```

Для сохранения распакованного источника добавьте `--copy`. Варианты категории вида `playhood_5` объединяются в базовый класс `playhood`; несколько классов сортируются и соединяются `_`. Изображения без аннотаций попадают в `images/no_annotations`.

Проверка датасета:

```powershell
python task2/validate_dataset.py task2/output/restructured_dataset/updated_annotations.json task2/output/restructured_dataset --output task2/output/dataset_report.json
```

Конвертация в YOLO:

```powershell
python task2/coco_to_yolo.py task2/output/restructured_dataset/updated_annotations.json task2/output/restructured_dataset task2/output/yolo_dataset
```

YOLO ID являются нулевыми и последовательными; соответствие исходным COCO ID записано в `classes.json`, порядок имён — в `classes.txt`. Пустым изображениям соответствуют пустые `.txt`. Рамки, частично выходящие за изображение, обрезаются по его границе и перечисляются в `clipped_annotation_ids`.

## Полученный результат

- XML: 3 423 изображения, из них 794 размечены; 2 001 фигура.
- COCO: 28 изображений, 40 аннотаций, 23 категории, 6 изображений без аннотаций.
- Все ссылки на файлы, `image_id` и `category_id` корректны.
- В исходном COCO найдена одна рамка, частично выходящая за изображение (`annotation_id=14`). Она сохранена в отчёте как предупреждение и безопасно обрезана при экспорте в YOLO.

## Тесты

```powershell
python -m unittest discover -s tests -v
```
