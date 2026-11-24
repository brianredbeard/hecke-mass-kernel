import HeckeMassKernel.Finite

namespace HeckeMassKernel.Scaffold

/-- The per-word operation used to verify the repository scaffold. -/
def probeSpec (word : UInt32) : UInt32 := word ^^^ 0xa5a5a5a5

def reference (words : List UInt32) : List UInt32 := words.map probeSpec

theorem reference_length (words : List UInt32) :
    (reference words).length = words.length := by
  simp [reference]

/-- The reference agrees with the specification at every index. -/
theorem reference_getElem? (words : List UInt32) (index : Nat) :
    (reference words)[index]? = words[index]?.map probeSpec := by
  simp [reference]

end HeckeMassKernel.Scaffold
