import tempfile

from pathlib import Path
from satellite._tables import Table


MINIMAL_TABLE_JAVA_FILE_LINES = (
    "@Entity",
    "@Table",
    "@Data",
    "@NoArgsConstructor",
    "public class Bed implements Serializable {",
    "",
    "    @Id",
    "    @GeneratedValue(strategy = GenerationType.AUTO)",
    "    private Long bedId;",
    "",
    "   @ManyToOne",
    '   @JoinColumn(name = "roomId", nullable = false)',
    "    private Room roomId;",
    "",
    "    @Column(nullable = false)",
    "    private String hl7String;",
    "",
    "    public Bed(String hl7String, Room roomId) {",
    "        this.hl7String = hl7String;",
    "        this.roomId = roomId;",
    "    }",
    "}",
)


def test_table_from_file():

    with tempfile.TemporaryDirectory() as dir_name:
        filepath = Path(dir_name, "Bed.java")
        with open(filepath, "w") as file:
            print("\n".join(MINIMAL_TABLE_JAVA_FILE_LINES), file=file)

        table = Table.from_java_file(filepath)

        assert table.name == "bed"
        assert len(table.columns) == 3
        assert table.n_rows == 0

        row = table.fake_row()
        assert row.id is None
        assert row.table_name == table.name
        assert row.n_rows == 1

        room_id_col = next(c for c in row.columns if c.name == "room_id")
        assert isinstance(row[room_id_col], int)
