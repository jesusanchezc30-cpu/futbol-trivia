import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(const FutbolTriviaApp());
}

class FutbolTriviaApp extends StatelessWidget {
  const FutbolTriviaApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Futbol Trivia',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF1B5E20)),
        useMaterial3: true,
      ),
      home: const PantallaInicio(),
    );
  }
}

class PantallaInicio extends StatelessWidget {
  const PantallaInicio({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFF1B5E20), Color(0xFF4CAF50)],
          ),
        ),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.sports_soccer, size: 100, color: Colors.white),
              const SizedBox(height: 20),
              const Text(
                'Futbol Trivia',
                style: TextStyle(
                  fontSize: 40,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: 10),
              const Text(
                'LaLiga Edition',
                style: TextStyle(fontSize: 18, color: Colors.white70),
              ),
              const SizedBox(height: 60),
              ElevatedButton(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => const MenuJuegos()),
                  );
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.white,
                  foregroundColor: const Color(0xFF1B5E20),
                  padding: const EdgeInsets.symmetric(horizontal: 50, vertical: 15),
                  textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                child: const Text('Jugar Solo'),
              ),
              const SizedBox(height: 15),
              OutlinedButton(
                onPressed: () {},
                style: OutlinedButton.styleFrom(
                  foregroundColor: Colors.white,
                  side: const BorderSide(color: Colors.white),
                  padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 15),
                  textStyle: const TextStyle(fontSize: 18),
                ),
                child: const Text('Multijugador'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class MenuJuegos extends StatelessWidget {
  const MenuJuegos({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Elige un juego'),
        backgroundColor: const Color(0xFF1B5E20),
        foregroundColor: Colors.white,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            _tarjetaJuego(context, 'Trivia', 'Preguntas de fútbol español', Icons.quiz, const Color(0xFF1565C0)),
            _tarjetaJuego(context, 'Adivina el jugador', 'Pistas progresivas', Icons.person_search, const Color(0xFF6A1B9A)),
            _tarjetaJuego(context, 'Adivina el escudo', 'Identifica el equipo', Icons.shield, const Color(0xFFE65100)),
            _tarjetaJuego(context, 'Completa el once', 'Forma el equipo titular', Icons.group, const Color(0xFF00695C)),
          ],
        ),
      ),
    );
  }

  Widget _tarjetaJuego(BuildContext context, String titulo, String subtitulo, IconData icono, Color color) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: ListTile(
        leading: CircleAvatar(backgroundColor: color, child: Icon(icono, color: Colors.white)),
        title: Text(titulo, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
        subtitle: Text(subtitulo),
        trailing: const Icon(Icons.arrow_forward_ios),
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => PantallaJuego(tipo: titulo)),
          );
        },
      ),
    );
  }
}

class PantallaJuego extends StatefulWidget {
  final String tipo;
  const PantallaJuego({super.key, required this.tipo});

  @override
  State<PantallaJuego> createState() => _PantallaJuegoState();
}

class _PantallaJuegoState extends State<PantallaJuego> {
  List preguntas = [];
  int indice = 0;
  int puntuacion = 0;
  bool cargando = true;
  String? seleccionada;
  bool respondida = false;

  @override
  void initState() {
    super.initState();
    cargarPreguntas();
  }

  Future<void> cargarPreguntas() async {
    final response = await http.get(
      Uri.parse('http://localhost:8000/preguntas?limite=10&tipo=trivia'),
    );
    if (response.statusCode == 200) {
      setState(() {
        preguntas = json.decode(response.body);
        cargando = false;
      });
    }
  }

  void responder(String opcion) {
    if (respondida) return;
    setState(() {
      seleccionada = opcion;
      respondida = true;
      if (opcion == preguntas[indice]['respuesta_correcta']) {
        puntuacion += 10;
      }
    });

    Future.delayed(const Duration(seconds: 1), () {
      if (indice < preguntas.length - 1) {
        setState(() {
          indice++;
          seleccionada = null;
          respondida = false;
        });
      } else {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (_) => PantallaResultado(puntuacion: puntuacion, total: preguntas.length * 10)),
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    if (cargando) return const Scaffold(body: Center(child: CircularProgressIndicator()));
    if (preguntas.isEmpty) return const Scaffold(body: Center(child: Text('No hay preguntas disponibles')));

    final pregunta = preguntas[indice];
    final opciones = List<String>.from(pregunta['opciones'] ?? []);

    return Scaffold(
      appBar: AppBar(
        title: Text('${indice + 1}/${preguntas.length}'),
        backgroundColor: const Color(0xFF1B5E20),
        foregroundColor: Colors.white,
        actions: [
          Padding(
            padding: const EdgeInsets.all(8),
            child: Center(child: Text('$puntuacion pts', style: const TextStyle(color: Colors.white, fontSize: 16))),
          )
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const SizedBox(height: 20),
            Card(
              color: const Color(0xFF1B5E20),
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Text(
                  pregunta['enunciado'],
                  style: const TextStyle(fontSize: 20, color: Colors.white, fontWeight: FontWeight.bold),
                  textAlign: TextAlign.center,
                ),
              ),
            ),
            const SizedBox(height: 30),
            ...opciones.map((opcion) {
              Color color = Colors.white;
              if (respondida) {
                if (opcion == pregunta['respuesta_correcta']) color = Colors.green.shade100;
                else if (opcion == seleccionada) color = Colors.red.shade100;
              }
              return Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: ElevatedButton(
                  onPressed: () => responder(opcion),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: color,
                    padding: const EdgeInsets.all(16),
                  ),
                  child: Text(opcion, style: const TextStyle(fontSize: 16, color: Colors.black87)),
                ),
              );
            }),
          ],
        ),
      ),
    );
  }
}

class PantallaResultado extends StatelessWidget {
  final int puntuacion;
  final int total;
  const PantallaResultado({super.key, required this.puntuacion, required this.total});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.emoji_events, size: 100, color: Colors.amber),
            const SizedBox(height: 20),
            const Text('¡Partida terminada!', style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold)),
            const SizedBox(height: 10),
            Text('$puntuacion / $total puntos', style: const TextStyle(fontSize: 24, color: Color(0xFF1B5E20))),
            const SizedBox(height: 40),
            ElevatedButton(
              onPressed: () => Navigator.popUntil(context, (route) => route.isFirst),
              style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF1B5E20), foregroundColor: Colors.white),
              child: const Text('Volver al inicio'),
            ),
          ],
        ),
      ),
    );
  }
}