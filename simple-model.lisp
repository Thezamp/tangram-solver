;;(clear-all)
(define-model simple-monk

   (sgp :mas 4 :act nil :esc t)

  (chunk-type puzzle-state)
  (chunk-type landmark piece location type)
  (chunk-type goal state)
  (chunk-type action piece location)

  (P retrieve-simple-landmark "optional comment string"
    =imaginal>
    =goal>
      isa goal
      state choose-landmark
    ?retrieval>
      state free
    ==>
    +retrieval>
      isa landmark
      type simple
  )

  (P retrieve-complex-landmark "optional comment string"
    =imaginal>
    =goal>
      state choose-c-landmark ;; don't use it now
    ?retrieval>
      state free
    ==>
    +retrieval>
      isa landmark
      type complex
  )

  (P landmark-to-goal "optional comment string"
    =retrieval>
      ISA  landmark

    =goal>
      state choose-landmark
    ==>
    =goal>  =retrieval

    )

;; "maybe add retrieval steps for errors in pieces and loc"
  (P decide-action
    =goal>
      ISA  landmark
      piece =p
      location =l
      type =t
    ?imaginal>
      state free

    ==>
    +imaginal>
      ISA  action
      piece =p
      location =l
      type =t
    +goal>
      isa goal
      state act
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
    !bind! =new-state ("update-state" (list =p =l =t))
    ;;+imaginal> =new-state
    =imaginal>
    =goal>
      isa goal
      state end
      ;;state choose-landmark

    )

)
