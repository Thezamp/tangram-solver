(clear-all)
(define-model simple-monk

   (sgp :mas 7 :act nil :esc t)
   (sgp :model-warnings nil)
   (sgp :v nil)
   (sgp :ans 0.2) ;;noise
   ;;(sgp :rt 1) ;;retrieval threshold

  (chunk-type puzzle-state pieces-remain)
  (chunk-type landmark piece location type)
  (chunk-type goal state)
  (chunk-type action piece location)
  (add-dm (UNF-REGION isa landmark piece LANDMARK-UNF location LANDMARK-UNF type UNFEASIBLE))
  (sdp UNF-REGION :base-level 0.5)
  
  (P completed "matches when no tans re left"
    =imaginal>
      pieces-remain nil
    =goal>
      isa goal
      state choose-landmark
    ==>
    =imaginal>
    =goal>
     state completed
  )

  (P retrieve-landmark "retrieves one of the landmarks using activation from imaginal"
    =imaginal>
      pieces-remain t
    =goal>
      isa goal
      state choose-landmark
    ?retrieval>
       state free

    ==>
    =imaginal>
    +retrieval>
      isa landmark
      :recently-retrieved nil
     =goal>
       state ldm-chosen
  )

  (p notice-error-and-backtrack "there are pieces left but no landmark"
   =imaginal>
     pieces-remain t

   =goal>
     isa goal
     state ldm-chosen
   ?retrieval>
      buffer failure

   ==>
   !output! BACKTRACK
   !bind! =new-state ("backtrack" =val)

   +goal>
     isa goal
     state choose-landmark
 )

 (P landmark-to-goal "a possible landmark is found, set it as goal"
   =retrieval>
     ISA  landmark

   =goal>
     state ret-to-goal
   ==>

   +goal>  =retrieval

   )

  ;;(spp notice-error :u 5)
  ;;(spp retrieve-simple-landmark :u 2)



  (P act-and-update "creates an action for the chosen landmark"
    =goal>
      ISA  landmark
      piece =p
      location =l

    ==>
    !output! =p
    !output! =l
    !bind! =new-state ("update" =p =l)

    +goal>
      isa goal
      state choose-landmark
  )


)
