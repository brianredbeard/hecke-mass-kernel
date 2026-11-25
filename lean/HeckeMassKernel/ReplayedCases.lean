import HeckeMassKernel.Finite

open HeckeMassKernel

namespace ReplayedCases

-- Recorded stabilizer orders, with both unit conventions.
private def masses : List (String × List Nat × String) :=
  [
    ("modular-23-full", [4, 2, 6], "11/12"),
    ("modular-23-projective", [2, 1, 3], "11/6"),
    ("modular-37-full", [2, 2, 2], "3/2"),
    ("modular-37-projective", [1, 1, 1], "3"),
    ("zi_rank2", [32], "1/32"),
    ("zi_rank3", [384], "1/384"),
    ("z12_rank2", [288], "1/288"),
    ("zi-determinant-five", [16, 8], "3/16")
  ]

private structure OperatorCase where
  name : String
  q : Nat
  rank : Nat
  destinations : List String
  expected : List (List Nat)

-- Each character is the zero-based target class of an edge in certificate order.
-- Singletons have only target 0. Matrices are the independently recorded outputs.
private def operators : List OperatorCase :=
  [
    ⟨"modular-23-2", 2, 2,
      ["101", "120", "111"],
      [[1, 2, 0], [1, 1, 1], [0, 3, 0]]⟩,
    ⟨"modular-23-3", 3, 2,
      ["1221", "0111", "0002"],
      [[0, 2, 2], [1, 3, 0], [3, 0, 1]]⟩,
    ⟨"modular-23-5", 5, 2,
      ["011011", "102102", "111111"],
      [[2, 4, 0], [2, 2, 2], [0, 6, 0]]⟩,
    ⟨"modular-23-7", 7, 2,
      ["01011001", "11012102", "12121111"],
      [[4, 4, 0], [2, 4, 2], [0, 6, 2]]⟩,
    ⟨"modular-23-11", 11, 2,
      ["111211221211", "001100112112", "100010011101"],
      [[0, 8, 4], [4, 6, 2], [6, 6, 0]]⟩,
    ⟨"modular-23-13", 13, 2,
      ["01020110021011", "11111120010121", "12202211100112"],
      [[6, 6, 2], [3, 9, 2], [3, 6, 5]]⟩,
    ⟨"modular-23-17", 17, 2,
      ["022002012111011011", "111001121100111112", "210111210000202221"],
      [[6, 8, 4], [4, 12, 2], [6, 6, 6]]⟩,
    ⟨"modular-23-19", 19, 2,
      ["21011120112101101121", "12011011021201010211", "11120111110110010102"],
      [[4, 12, 4], [6, 10, 4], [6, 12, 2]]⟩,
    ⟨"modular-23-29", 29, 2,
      ["011111201101121011101122212011", "111101100210212121000011121102", "100212010111101112111000111101"],
      [[6, 18, 6], [9, 15, 6], [9, 18, 3]]⟩,
    ⟨"modular-23-31", 31, 2,
      ["11100101012111000011121010100111", "10110012111222100122211121001100", "21011121121111111111112112111010"],
      [[12, 18, 2], [9, 15, 8], [3, 24, 5]]⟩,
    ⟨"modular-23-37", 37, 2,
      ["01101112111022112212110211100111102000", "11012121210011101121201110100121011101", "10021211101110001110112000211212020112"],
      [[10, 20, 8], [10, 22, 6], [12, 18, 8]]⟩,
    ⟨"modular-23-41", 41, 2,
      ["020111110011201121212121221122101001011011", "110200201120110112111111111011002111100112", "201110101210110201120002000100111212110221"],
      [[10, 22, 10], [11, 25, 6], [15, 18, 9]]⟩,
    ⟨"modular-23-43", 43, 2,
      ["01111012100110211012210111111012020210111120", "12002101111101122101100100102111011111220211", "11101110211211011211011201201200112001110102"],
      [[12, 24, 8], [12, 24, 8], [12, 24, 8]]⟩,
    ⟨"modular-23-47", 47, 2,
      ["101122011112121121000101101000121121211110221101", "101111102001112112111002200111211211100201111100", "210201211101001011212011110212110100101112102010"],
      [[12, 26, 10], [13, 27, 8], [15, 24, 9]]⟩,
    ⟨"modular-37-2", 2, 2,
      ["012", "022", "011"],
      [[1, 1, 1], [1, 0, 2], [1, 2, 0]]⟩,
    ⟨"modular-37-3", 3, 2,
      ["0210", "2022", "1101"],
      [[2, 1, 1], [1, 0, 3], [1, 3, 0]]⟩,
    ⟨"modular-37-5", 5, 2,
      ["221100", "012202", "110210"],
      [[2, 2, 2], [2, 1, 3], [2, 3, 1]]⟩,
    ⟨"modular-37-7", 7, 2,
      ["10201212", "20122001", "01002121"],
      [[2, 3, 3], [3, 2, 3], [3, 3, 2]]⟩,
    ⟨"modular-37-11", 11, 2,
      ["220000012011", "010222221022", "111010101122"],
      [[6, 3, 3], [3, 2, 7], [3, 7, 2]]⟩,
    ⟨"modular-37-13", 13, 2,
      ["21212011220211", "00121022002102", "12001120110020"],
      [[2, 6, 6], [6, 3, 5], [6, 5, 3]]⟩,
    ⟨"modular-37-17", 17, 2,
      ["100012002100010220", "221121201201220110", "202021021212021111"],
      [[10, 4, 4], [4, 7, 7], [4, 7, 7]]⟩,
    ⟨"modular-37-19", 19, 2,
      ["11021000201202021120", "02100012112120212210", "22012221002011110012"],
      [[8, 6, 6], [6, 7, 7], [6, 7, 7]]⟩,
    ⟨"modular-37-23", 23, 2,
      ["210210000210212002010010", "120121201121001211220201", "002122012120120101122122"],
      [[12, 6, 6], [6, 10, 8], [6, 8, 10]]⟩,
    ⟨"modular-37-29", 29, 2,
      ["110121202121121222011012222100", "000012111012002111022101100201", "222200101212212000202020011020"],
      [[6, 12, 12], [12, 12, 6], [12, 6, 12]]⟩,
    ⟨"modular-37-31", 31, 2,
      ["00112002202112212200101221112121", "02220020111220021001212000021212", "10001211121021100120200112220010"],
      [[8, 12, 12], [12, 8, 12], [12, 12, 8]]⟩,
    ⟨"modular-37-41", 41, 2,
      ["201221112022102001220111210211112222021121", "022112021000211222002220021022201001002200", "110000200111020100110022122100021111110012"],
      [[8, 17, 17], [17, 8, 17], [17, 17, 8]]⟩,
    ⟨"modular-37-43", 43, 2,
      ["02200011120120120010021022001021022100102001", "20112222010211211122012111210010201210201200", "01121020211210212021202201022102011221010122"],
      [[20, 12, 12], [12, 17, 15], [12, 15, 17]]⟩,
    ⟨"modular-37-47", 47, 2,
      ["200011102022210220002010202112201110010020122111", "120122000201120102210120120020022222021212211220", "111220211111101110021201001221102201102001210002"],
      [[18, 15, 15], [15, 12, 21], [15, 21, 12]]⟩,
    ⟨"zi_rank2-3-place-1", 3, 2,
      ["000000000000"],
      [[12]]⟩,
    ⟨"zi_rank2-5-place-2", 5, 2,
      ["000000"],
      [[6]]⟩,
    ⟨"zi_rank2-5-place-3", 5, 2,
      ["000000"],
      [[6]]⟩,
    ⟨"zi_rank3-3-place-1", 3, 3,
      ["000000000000000000000000000000000000000000000000000000000000000000000000000000000000"],
      [[84]]⟩,
    ⟨"zi_rank3-5-place-2", 5, 3,
      ["0000000000000000000000000000000"],
      [[31]]⟩,
    ⟨"zi_rank3-5-place-3", 5, 3,
      ["0000000000000000000000000000000"],
      [[31]]⟩,
    ⟨"z12_rank2-2-place-1", 2, 2,
      ["000000"],
      [[6]]⟩,
    ⟨"z12_rank2-3-place-2", 3, 2,
      ["000000000000"],
      [[12]]⟩,
    ⟨"z12_rank2-5-place-3", 25, 2,
      ["00000000000000000000000000"],
      [[26]]⟩,
    ⟨"z12_rank2-5-place-4", 25, 2,
      ["00000000000000000000000000"],
      [[26]]⟩,
    ⟨"zi-determinant-five-13", 13, 2,
      ["00111011011100", "10101101101111"],
      [[6, 8], [4, 10]]⟩,
    ⟨"zi-determinant-five-17", 17, 2,
      ["011111111111111110", "100010100111010111"],
      [[2, 16], [8, 10]]⟩
  ]

private def matMul (a b : List (List Nat)) : List (List Nat) :=
  let cols := (List.range b.length).map (fun j => b.map (fun row => row.getD j 0))
  a.map (fun row => cols.map (fun col => (row.zip col).foldl (fun acc (x, y) => acc + x * y) 0))

private def checkDetailedBalance (name : String) (orders : List Nat) (matrix : List (List Nat)) :
    IO Unit := do
  let n := orders.length
  unless matrix.length == n do
    throw (IO.userError s!"{name}: matrix size does not match stabilizer orders")
  for i in List.range n do
    let rowI := matrix.getD i []
    let dI := orders.getD i 0
    for j in List.range n do
      let rowJ := matrix.getD j []
      let dJ := orders.getD j 0
      let bij := rowI.getD j 0
      let bji := rowJ.getD i 0
      unless dJ * bij == dI * bji do
        throw (IO.userError
          s!"{name}: detailed balance failed at ({i}, {j}): {dJ}*{bij} ≠ {dI}*{bji}")

private def checkFamily (family : String) (orders : List Nat) (checkPrimeRowSum : Bool) :
    IO Unit := do
  let members := operators.filter (fun op => op.name.startsWith family)
  for op in members do
    checkDetailedBalance op.name orders op.expected
    if checkPrimeRowSum then
      for row in op.expected do
        let rowSum := row.foldl (· + ·) 0
        unless rowSum == op.q + 1 do
          throw (IO.userError s!"{op.name}: expected row sum {op.q + 1}, got {rowSum}")
  for a in members do
    for b in members do
      unless matMul a.expected b.expected == matMul b.expected a.expected do
        throw (IO.userError s!"{a.name} and {b.name} do not commute")

private def check (name expected : String) (result : Frac) : IO Unit := do
  let actual := result.render
  unless actual == expected do
    throw (IO.userError s!"{name}: expected {expected}, got {actual}")

def emit : IO Unit := do
  checkFamily "modular-23-" [4, 2, 6] true
  checkFamily "modular-37-" [2, 2, 2] true
  checkFamily "zi-determinant-five-" [16, 8] false
  for (name, orders, expected) in masses do
    check name expected (classMass orders)
    let args := String.intercalate " " (orders.map toString)
    IO.println s!"mass\t{args}\t{expected}"
  for op in operators do
    let size := op.expected.length
    unless op.destinations.length == size do
      throw (IO.userError s!"{op.name}: wrong matrix height")
    for (row, expectedRow) in op.destinations.zip op.expected do
      unless expectedRow.length == size && row.toList.all
          (fun c => '0'.toNat ≤ c.toNat && c.toNat < '0'.toNat + size) do
        throw (IO.userError s!"{op.name}: invalid row or destination index")
      for (expected, target) in expectedRow.zipIdx do
        let label := Char.ofNat ('0'.toNat + target)
        let samples := row.toList.map
          (fun c => Frac.integer (if c == label then 1 else 0))
        let u := Frac.integer 1
        check op.name (toString expected) (hecke u op.q 0 op.rank samples)
        let args := String.intercalate " "
          ([u.render, toString op.q, "0", toString op.rank] ++ samples.map Frac.render)
        IO.println s!"hecke\t{args}\t{expected}"

end ReplayedCases
