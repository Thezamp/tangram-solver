The project folder needs to be in the ACT-R distribution folder so ACT-R/tangram-solver

An example can be run as
import actr
import monk_oop

m=monk_oop.Monk("ACT-R:tangram-solver;simple-model.lisp")
m.run(10) ##atm it runs in ~9.6 sec