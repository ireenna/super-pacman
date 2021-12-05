sbcl --load quicklisp.lisp
(quicklisp-quickstart:install :path "E:/3-course/IIS/my-pacman/quicklisp.lisp")
(ql:quickload "cl-csv")
(defparameter data (cl-csv:read-csv #P"E:/3-course/IIS/my-pacman/result.csv"))

(defparameter score ())
(loop for a in data  do (push (nth 0 (with-input-from-string (in (nth 4 a))
  (loop for x = (read in nil nil) while x collect x))) score))

(defparameter times ())
(loop for a in data  do (push (NTH 0 (with-input-from-string (in ( String-left-trim "0:00:" (NTH 2 a)))
  (loop for x = (read in nil nil) while x collect x))) times))

(defparameter time_exp (/ (apply '+ times) (length times)))

(defparameter score_mean (/ (apply '+ score) (length score)))

(defparameter score_dispersion (/ (apply '+ (mapcar (lambda (x) (* x x)) (mapcar (lambda (n) (- n score_mean))
        score))) (length score)))

time_exp
score_dispersion