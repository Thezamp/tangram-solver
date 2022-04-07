;;(clear-all)
(define-model simple-monk

   (sgp :mas 4 :act nil :esc t)

  (chunk-type puzzle-state finished)
  (chunk-type landmark piece location type)
  (chunk-type goal state)
  (chunk-type action piece location)

  (P completed "optional comment string"
    =imaginal>
      finished t
    =goal>
      isa goal
      state choose-landmark
    ==>
    =imaginal>
    =goal>
     state completed
  )

  (P retrieve-simple-landmark "optional comment string"
    =imaginal>
      - finished t
    =goal>
      isa goal
      state choose-landmark
    ?retrieval>
       state free

    ==>
    =imaginal>
    +retrieval>
      isa landmark
      - type nil
      ;;type =type ;; not used currently
      :recently-retrieved nil
     =goal>
       state ret-to-goal
  )

  (P retrieve-complex-landmark "optional comment string"
    =imaginal>
      - finished t
    =goal>
      state choose-complex-landmark ;; not using it
    ?retrieval>
      state free
    ==>
    =imaginal>
    +retrieval>
      isa landmark
      type complex
      :recently-retrieved nil
    =goal>
       state ret-to-goal
  )

  (P landmark-to-goal "optional comment string"
    =retrieval>
      ISA  landmark

    =goal>
      state ret-to-goal
    ==>

    +goal>  =retrieval

    )

;; "maybe add retrieval steps for errors in pieces and loc"
  (P decide-action
    =goal>
      ISA  landmark
      - piece ERROR
      piece =p
      location =l
      type =t
    ?imaginal>
      state free

    ==>
    !output! =p
    !output! =l
    +imaginal>
      ISA  action
      piece =p
      location =l
      type =t
    +goal>
      isa goal
      state act
    )

  (p decide-backtrack
    =goal>
      isa   landmark
      piece error
      piece =val
    ?imaginal>
      state free
    ==>
    !output! BACKTRACK
    !bind! =new-state ("backtrack" =val)
    ;;=imaginal>
    +goal>
      isa goal
      state choose-landmark
  )

  (P update "optional comment string"
    =imaginal>
      ISA  action
      piece =p
      location =l
      type =t
    =goal>
      state act
    ==>
    !bind! =new-state ("update" =p =l)
    ;;+imaginal> =new-state
    =imaginal>
    +goal>
      isa goal
      ;;state end
      state choose-landmark

    )

)
