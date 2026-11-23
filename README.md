# UVM Assembler (Вариант №13)

Ассемблер для учебной виртуальной машины (УВМ). Этап 1: трансляция
CSV-программы в промежуточное представление и (опционально) в
двоичный файл.

## Установка и запуск

```bash
python -m src.cli examples/spec_tests.csv out.bin --test
make test
```

## Язык ассемблера

Формат CSV: `OPCODE, operand1, operand2, ...`. Строки, начинающиеся с
`#`, и пустые строки игнорируются. Команда занимает 4 байта.

### Команды

| Мнемоника | Формат CSV | Биты |
|---|---|---|
| `LOAD_CONST` | `LOAD_CONST, addr, const` | A=31 (0..4), B=addr (5..7), C=const (8..15) |
| `LOAD_MEM` | `LOAD_MEM, offset, src, dst` | A=18, B=offset (5..7), C=src (19..21), D=dst (22..24) |
| `STORE_MEM` | `STORE_MEM, src, dst` | A=1, B=src (5..7), C=dst (8..10) |
| `BITREVERSE` | `BITREVERSE, src, base, off` | A=2, B=src (5..7), C=base (8..10), D=off (11..23) |

## Тесты спецификации

| Команда | Вход | Байты |
|---|---|---|
| `LOAD_CONST` | `A=31, B=3, C=62` | `7F 3E 00 00` |
| `LOAD_MEM` | `A=18, B=484, C=4, D=0` | `92 3C 20 00` |
| `STORE_MEM` | `A=1, B=5, C=6` | `A1 06 00 00` |
| `BITREVERSE` | `A=2, B=3, C=5, D=222` | `62 F5 06 00` |

## Режим тестирования

С `--test` на экран выводится промежуточное представление:

```
01: LOAD_CONST: A=31, B=3, C=62
02: LOAD_MEM: A=18, B=484, C=4, D=0
03: STORE_MEM: A=1, B=5, C=6
04: BITREVERSE: A=2, B=3, C=5, D=222
```

## Машинный код (этап 2)

- Команда — 4 байта, little-endian.
- Кодирование вынесено в `src/encoder.py`:
  `encode_command`, `encode_program`, `format_byte_dump`.
- Число ассемблированных команд всегда печатается в конце работы CLI.
- С флагом `--test` печатаются и IR, и байтовый дамп.

Пример вывода:

```
01: LOAD_CONST: A=31, B=3, C=62
02: LOAD_MEM: A=18, B=484, C=4, D=0
03: STORE_MEM: A=1, B=5, C=6
04: BITREVERSE: A=2, B=3, C=5, D=222
01: 7F 3E 00 00
02: 92 3C 20 00
03: A1 06 00 00
04: 62 F5 06 00
assembled 4 command(s) -> out.bin
```

## Интерпретатор (этап 3)

```bash
python -m src.cli examples/copy_array.csv out_copy.bin
python -m src.interpreter out_copy.bin dump.json --start 0 --end 16
cat dump.json
```

Дамп памяти — JSON:

```json
{
  "range": {"start": 0, "end": 16},
  "memory": [11, 22, 33, 44, 0, 0, 0, 0, 11, 22, 33, 44, 0, 0, 0, 0]
}
```

Модель памяти:

- `MEMORY_SIZE = 256` байт данных;
- 8 восьмибитных регистров;
- память команд (`state.program`) отделена от памяти данных.

## АЛУ: bitreverse() (этап 4)

Команда `BITREVERSE, src, base, off` вычисляет
`mem[reg[base] + off] = bitreverse(reg[src])`, где `bitreverse`
переворачивает порядок бит в 8-битном слове.

Пример:

```bash
make run-alu
```

Ожидаемые значения в дампе:

| Адрес | Вход | Результат |
|---|---|---|
| 8 | 176 (0b10110000) | 13 (0b00001101) |
| 9 | 15  (0b00001111) | 240 (0b11110000) |
| 10 | 129 (0b10000001) | 129 (0b10000001) |