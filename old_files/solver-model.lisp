(clear-all)
(define-model solver

  (sgp :mas 7 :act nil :esc t) ;; associative str, ??, subsybolic compt
  (sgp :model-warnings nil)
  (sgp :v t) ;; trace
  (sgp :ans 0.2) ;; noise
  ;; (sgp :ga 3) ;; goal activation is used for trying to retrieve a piece, or fail
  (sgp :rt 0.5) ;; retrieval threshold


  (chunk-type goal state piece-type location)
  (chunk-type landmark piece-type grid orientation)
  (chunk-type puzzle-state
    PIECES-AVAILABLE
    LANDMARK-1 LANDMARK-2 LANDMARK-3 LANDMARK-4 LANDMARK-5 LANDMARK-6
    SPECIAL-LANDMARK
    )


  (add-dm
    (UNF-REG ISA LANDMARK piece-type UNF-PIECE grid BACKTRACK  )

  )


(P completed "all pieces have been used"
  =imaginal>
    ISA  puzzle-state
    pieces-available nil
  =goal>
    ISA goal
    state choose-landmark
  ==>
  =imaginal>
  =goal>
    state stop
  )

(P retrieve-landmark "choose a landmark thanks to activation"
  =imaginal>
    ISA  puzzle-state
    pieces-available t
  =goal>
    isa goal
    state choose-landmark

  ?retrieval>
    state free
  ==>
  +retrieval>
    ISA  landmark
    - piece-type nil
    ;; :recently-retrieved nil
  =imaginal>
  =goal>
    state act-on-landmark
  )

(P unfeasible-region-found "the problem landmark is matched"
  =goal>
    ISA  goal
    state act-on-landmark
  =imaginal>
  =retrieval>
    piece-type UNF-PIECE
  ==>
  !bind! =res ("region-backtrack")
  =imaginal>
  =goal>
    ISA  goal
    ;;state resolve-problem
    state wait
  )

(P still-unfeasible "problem is still present"
  =goal>
    ISA  goal
    state resolve-problem
  =imaginal>
    SPECIAL-landmark unf-reg
  ==>
  !bind! =res ("region-backtrack")
  =imaginal>
  =goal>
    ISA  goal
    state resolve-problem
  )

(P region-removed "now it's feasible again"
  =goal>
    ISA  goal
    state resolve-problem
  =imaginal>
    SPECIAL-landmark unf-reg
  ==>
  =imaginal>
  =goal>
    state choose-landmark
  )

(P fail-to-retrieve "only weak landmarks are left and a failure happens"
  =retrieval>
    buffer failure
  =goal>
  ==>
  !bind! =res ("piece-backtrack")
  =goal>
    state choose-landmark
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
    orientation =o
  ==>
  !bind! =res ("update" =p =g =o)
  =goal>
    ISA  goal
    state wait
  )

)
