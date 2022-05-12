 (clear-all)
(define-model two-backtrack
    (sgp :mas 7 :act nil :esc t) ;; associative str, ??, subsybolic compt
    (sgp :model-warnings nil)
    (sgp :v nil) ;; trace
    (sgp :ans 0.2) ;; noise
    (sgp :ga 3) ;; goal activation is used for trying to retrieve a piece, or fail
    (sgp :rt 0.5) ;; retrieval threshold

    (chunk-type landmark piece-type location type)
    (chunk-type process-goal state piece-type location)
    ;;(chunk-type landmark-goal state piece-type location)
    (chunk-type action piece location)
    (chunk-type puzzle-state pieces-available )
    (chunk-type piece-state BIG-T MEDIUM-T SMALL-T SQUARE PARALL)
    (chunk-type piece name type)


    (add-dm
    (BIG-T1 ISA PIECE NAME BIG-T1 TYPE BIG-T)
    (BIG-T2 ISA PIECE NAME BIG-T2 TYPE BIG-T)
    (MEDIUM-T ISA PIECE NAME MEDIUM-T TYPE MEDIUM-T)
    (SQUARE ISA PIECE NAME SQUARE TYPE SQUARE)
    (PARALL ISA PIECE NAME PARALL TYPE PARALL)
    (SMALL-T1 ISA PIECE NAME SMALL-T1 TYPE SMALL-T)
    (SMALL-T2 ISA PIECE NAME SMALL-T2 TYPE SMALL-T)
    (UNF-REGION ISA LANDMARK piece-type UNF-REGION LOCATION BACKTRACK TYPE UNF-REGION)
    )

    (P completed "all pieces have been used"
        =imaginal>
            isa puzzle-state
            pieces-available nil
        =goal>
            isa process-goal
            state choose-landmark
        ==>
        !output! PROBLEM-COMPLETED
        =imaginal>
        =goal>
            state complete
    )

    (P retrieve-landmark "retrieves a landmark depending on type and presence in imaginal"
        =imaginal>
            isa puzzle-state
            pieces-available t

        =goal>
            isa process-goal
            state choose-landmark
        ?retrieval>
            state free
        ==>
        +retrieval>
            isa landmark
            ;; - location nil
            :recently-retrieved nil
        =imaginal>
        =goal>
            state focus-landmark
    )


    (P  landmark-to-goal
        =goal>
            isa process-goal
            state focus-landmark
        =retrieval>
            isa landmark
            piece-type =p
            location =l
        ==>
        !bind! =res ("get-pieces") ;;update the imaginal buffer
        +goal>
            isa process-goal
            state search
            piece-type =p
            location =l
    )

    (P unfeasible-region-found
        =goal>
            isa process-goal
            state search
            piece-type UNF-REGION
        ==>
        !output! UNFEASIBLE-REGION-FOUND
        !bind! =res ("region-backtrack")
        +goal>
            isa process-goal
            state choose-landmark

    )

    (P try-retrieve-piece
        =goal>
            isa process-goal
            state search
            piece-type =p
            - piece-type UNF-REGION
            - piece-type COMPOUND
        =imaginal> ;; pieces of that type are left
            isa piece-state
            =p t

        ?retrieval>
            state free
        ==>
        =goal>
            state act
        +retrieval>
            isa piece
            type =p
        =imaginal>
    )

    (P compound-to-expand "a compound ldm is found"
      =goal>
          isa process-goal
          state search
          piece-type COMPOUND
          piece-type =p
          location =l
      ==>
      !bind! =res ("update" =p =l)
      +goal>
          isa process-goal
          state choose-landmark
      )

    (P no-piece "the chosen piece is not available"
        =goal>
            isa process-goal
            state search
            piece-type =p
            - piece-type COMPOUND
            - piece-type UNF-REGION
        =imaginal> ;; pieces of that type are left
            =p nil
        ==>
        !bind! =res ("piece-backtrack")
        +goal>
            isa process-goal
            state choose-landmark
        =imaginal>  ;;otherwise probably gets harvested
    )

    (p  backtrack-due-to-failure "happens both for landmarks and piece"
        =retrieval>
            buffer  failure
        =goal>
            state free
        ==>
        !bind! =res ("piece-backtrack")
        +goal>
            isa process-goal
            state choose-landmark
    )


    (P act-and-update "piece found, proceed"
        =goal>
            isa process-goal
            piece-type =p
            location =l
            state act
        =retrieval>
            isa piece
            type =p
        ==>
        !bind! =res ("update" =p =l)
        ;;!bind! =new ("update" =p =l)
        +goal>
            isa process-goal
            state choose-landmark
    )
)

    (P  no-ldm-alternatives
        =goal>
            ;; isa process-goal
            isa keep-for-reference
            state choose-landmark
        =retrieval>
            buffer  failure
        ==>
        !bind! =res ("piece-backtrack")
        +goal>
            isa process-goal
            state choose-landmark
    )

    (P failed-to-retrieve "did not see the piece"
        =goal>
            ;;isa landmark-goal
            isa keep-for-reference
            state act
        =retrieval>
            buffer  failure
        ==>
        !bind! =res ("piece-backtrack")
        +goal>
            isa process-goal
            state choose-landmark
    )
