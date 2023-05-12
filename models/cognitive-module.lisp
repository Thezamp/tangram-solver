(clear-all)
(define-model solver

  (sgp :mas 8 :act nil :esc t) ;; associative str, ??, subsybolic compt
  (sgp :model-warnings nil)
  (sgp :v t) ;; trace
  (sgp :bll nil) ;; base-level-learning
  (sgp :ans 0.2) ;; noise
  ;; (sgp :ga 3) ;; goal activation is used for trying to retrieve a piece, or fail
  ;;(sgp :rt 2.5) ;; retrieval threshold
  (sgp :declarative-num-finsts 3)
  ;;(sgp :bll 0.5 :ol t)

  (chunk-type goal state piece-type location)
  (chunk-type landmark piece-type x y grid rotation)
  (chunk-type puzzle-state
    PIECES-AVAILABLE
    LANDMARK-1 LANDMARK-2 LANDMARK-3 LANDMARK-4 LANDMARK-5 LANDMARK-6
    SPECIAL-LANDMARK
    )

    (add-dm
      (UNF-REG ISA LANDMARK piece-type UNF-PIECE grid nil  )
      (is-backtracking isa goal state solve-problem)
      (retrieve-ignoring-finsts isa goal state retrieve-ignoring)
    )

(P completed "all pieces have been used"
  =imaginal>
    ISA  puzzle-state
    pieces-available nil
  =goal>
    ISA goal
    state choose-landmark
  ==>
  !bind! =res ("flag-completed")
  =imaginal>
  =goal>
    state stop
  )


(P fail-to-retrieve "only weak landmarks are left or a failure happens"
  ?retrieval>
    buffer failure
  =goal>
  ==>
  !bind! =res ("piece-backtrack")
  =goal>
    state wait
  )

  (P no-landmarks "pieces are available but cannot find any landmark"
  =imaginal>
    pieces-available t
    landmark1 nil
  =goal>
    state choose-landmark
  ==>
  !bind! =res ("piece-backtrack")
  =goal>
    state wait
  )

(P notice-problem "instead of landmarks, notice unfeasibility"
  =imaginal>
    ISA puzzle-state
    - SPECIAL-LANDMARK nil
  =goal>
    ISA goal
    state choose-landmark
  ==>
  =imaginal>
  =goal>
    ISA  goal
    state solve-problem
  )

(P unfeasible-region-found "the problem landmark is found"
  =goal>
    ISA  goal
    state solve-problem
  =imaginal>
    isa puzzle-state
    - SPECIAL-LANDMARK nil

  ==>
  !bind! =res ("region-backtrack")
  =imaginal>
  =goal>
    isa goal
    state wait
  )

(P region-removed "now it's feasible again"
  =goal>
    ISA  goal
    state solve-problem
  =imaginal>
    SPECIAL-LANDMARK nil
  ==>
  =imaginal>
  =goal>
    state choose-landmark
  )

(P retrieve-landmark "choose a landmark thanks to activation"
  =imaginal>
    ISA  puzzle-state
    pieces-available t
    - landmark-1 nil
  =goal>
    isa goal
    state choose-landmark

  ?retrieval>
    state free
  ==>
  +retrieval>
    ISA  landmark
    - piece-type nil
    - piece-type UNF-PIECE
    :recently-retrieved nil
  =imaginal>

  =goal>
    state act-on-landmark
  )

(p retrieve-any-landmark "accept landmarks recently used"
  =imaginal>
    ISA  puzzle-state
    pieces-available t
  ;;  - landmark-1 nil
  =goal>
    isa goal
    state retrieve-ignoring

  ?retrieval>
    state free
  ==>
  +retrieval>
    ISA  landmark
    - piece-type nil
    - piece-type UNF-PIECE
  =imaginal>

  =goal>
    state act-on-landmark
)

(P act-and-update "act on the landmark"
  =goal>
    ISA  goal
    state act-on-landmark
  =retrieval>
    isa landmark
    piece-type =p
    - piece-type UNF-PIECE
    grid =g
    rotation =r
  ==>

  !bind! =res ("update" =p =g =r)
  =goal>
    ISA  goal
    state wait
  )

(spp notice-problem :u 1.5)
(spp retrieve-landmark :u 1)
)
