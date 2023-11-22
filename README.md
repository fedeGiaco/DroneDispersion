# DroneDispersion
Tesi triennale per Ingegneria Informatica 2022/23, UNIPI.
Sviluppo su piattaforma autopilota di un meccanismo di dispersione di sciami di droni basato sul feromone repulsivo.

Dato uno sciame, ogni drone decolla e si dirige in una direzione casuale rilasciando una traccia repulsiva.
La traccia non è attraversabile se recente. Se un drone si avvicina troppo a una traccia altrui recente, cambia direzione (sempre casuale).
Una volta che tutti i droni si sono fermati, questi ripartano in nuove direzioni (sempre casuali) fino a un certo numero di iterazioni.
Terminate, lo sciame atterra e viene mostrata la distanza percorsa singolarmente e totale di tutti i droni.

L'algoritmo è funzionante.
