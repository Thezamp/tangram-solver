;;(clear-all)
(define-model simple-monk

   (sgp :mas 4 :act nil :esc t)

  (chunk-type puzzle-state finished)
  (chunk-type landmark piece location type)
  (chunk-type goal state)
  (chunk-type action piece location)

  (P completed "matches when no landmarks are visible"
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

  (P retrieve-simple-landmark "retrieves one of the landmark using activation from imaginal"
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

  (P retrieve-complex-landmark "currently not used"
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

  (P landmark-to-goal "the chosen landmark gets into the goal buffer"
    =retrieval>
      ISA  landmark

    =goal>
      state ret-to-goal
    ==>

    +goal>  =retrieval

    )

;; "maybe add retrieval steps for errors in pieces and loc"
  (P decide-action "creates an action for the chosen landmark"
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

  (p decide-backtrack "if an error landmark is found,backtrack"
    =goal>
      isa   landmark
      piece error
      piece =val
    ?imaginal>
      state free
    ==>
    !output! BACKTRACK
    !bind! =new-state ("backtrack" =val)
    ;;likely enough to eval, but possibly create the imaginal chunk here in the
    ;;future
    +goal>
      isa goal
      state choose-landmark
  )

  (P update "If an action is chosen, the state is updated accordingly"
    =imaginal>
      ISA  action
      piece =p
      location =l
      type =t
    =goal>
      state act
    ==>
    !bind! =new-state ("update" =p =l)
    ;;same reasoning of the backtrack prduction
    =imaginal>
    +goal>
      isa goal
      state choose-landmark

    )

)
