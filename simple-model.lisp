(clear-all)
(define-model simple-monk

   (sgp :mas 7 :act nil :esc t)
   (sgp :model-warnings nil)
   (sgp :v nil)
   (sgp :ans 0.2) ;;noise

  (chunk-type puzzle-state finished)
  (chunk-type landmark piece location type)
  (chunk-type goal state)
  (chunk-type action piece location)
  (add-dm (LDM-ERROR isa landmark piece LANDMARK-ERROR location LANDMARK-ERROR type LANDMARK-ERROR))

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

  (p notice-error "retrieves error landmark"
   =imaginal>
     - finished t
     LDM-ERROR LDM-ERROR
   =goal>
     isa goal
     state choose-landmark
   ?retrieval>
      state free

   ==>
   =imaginal>
   +retrieval>
     isa landmark
     type LANDMARK-ERROR
    =goal>
      state ret-to-goal
 )

  (P retrieve-simple-landmark "retrieves one of the landmark using activation from imaginal"
    =imaginal>
      - finished t
      LDM-ERROR NIL
    =goal>
      isa goal
      state choose-landmark
    ?retrieval>
       state free

    ==>
    =imaginal>
    +retrieval>
      isa landmark
      type SIMPLE
      ;;type =type ;; not used currently
      :recently-retrieved nil
     =goal>
       state ret-to-goal
  )

  ;;(spp notice-error :u 5)
  ;;(spp retrieve-simple-landmark :u 2)

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
      state placeholder
      ISA  landmark
      - piece LANDMARK-ERROR
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

    (P act-and-update "creates an action for the chosen landmark"
      =goal>
        ISA  landmark
        - piece LANDMARK-ERROR
        piece =p
        location =l
        ;;type =t

      ==>
      !output! =p
      !output! =l
      !bind! =new-state ("update" =p =l)

      +goal>
        isa goal
        state choose-landmark
    )

  (p decide-backtrack "if an error landmark is found,backtrack"
    =goal>
      isa   landmark
      piece LANDMARK-ERROR
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
