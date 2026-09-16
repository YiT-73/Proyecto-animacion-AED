#include <iostream>
#include <functional>
#include <stdexcept>
#include <random>
#include <string>
#include <utility>
#include <cmath>

using namespace std;

// ============================================================
// HASH BASE
// Convierte cualquier Key en un size_t usando std::hash
// ============================================================
template <typename Key>
size_t base_hash(const Key& key) {
    return std::hash<Key>{}(key);
}

// ============================================================
// 1) HASH POR DIVISIÓN
// h(k) = k mod m
// ============================================================
template <typename Key>
class DivisionHash {
public:
    size_t operator()(const Key& key, size_t tableSize) const {
        return base_hash(key) % tableSize;
    }
};

// ============================================================
// 2) HASH POR MULTIPLICACIÓN
// h(k) = floor( m * frac(kA) )
// ============================================================
template <typename Key>
class MultiplicationHash {
private:
    double A;

public:
    explicit MultiplicationHash(double a = 0.6180339887) : A(a) {
        if (A <= 0.0 || A >= 1.0) {
            throw invalid_argument("A debe cumplir 0 < A < 1");
        }
    }

    size_t operator()(const Key& key, size_t tableSize) const {
        size_t k = base_hash(key);
        double x = k * A;
        double fractional = x - floor(x);
        return static_cast<size_t>(floor(tableSize * fractional));
    }
};

// ============================================================
// 3) HASH UNIVERSAL
// h(k) = ((a*k + b) mod p) mod m
// ============================================================
template <typename Key>
class UniversalHash {
private:
    size_t a;
    size_t b;
    size_t p;

public:
    explicit UniversalHash(size_t prime = 1000003) : p(prime) {
        if (p < 2) {
            throw invalid_argument("p debe ser un primo >= 2");
        }

        random_device rd;
        mt19937 gen(rd());

        uniform_int_distribution<size_t> distA(1, p - 1);
        uniform_int_distribution<size_t> distB(0, p - 1);

        a = distA(gen);
        b = distB(gen);
    }

    size_t operator()(const Key& key, size_t tableSize) const {
        size_t k = base_hash(key);
        return ((a * k + b) % p) % tableSize;
    }

    size_t getA() const { return a; }
    size_t getB() const { return b; }
    size_t getP() const { return p; }
};

// ============================================================
// TABLA HASH CON CHAINING
// - Lista simplemente enlazada por bucket
// - Inserción en cabeza
// - Rehash al exceder maxFillFactor
// - FillFactor = elements / (capacity * k)
// ============================================================
template <typename Key, typename Value, typename HashPolicy = DivisionHash<Key>>
class HashTable {
private:
    // -----------------------------
    // Nodo de lista simplemente enlazada
    // -----------------------------
    struct Node {
        Key key;
        Value value;
        Node* next;

        Node(const Key& k, const Value& v, Node* n = nullptr)
            : key(k), value(v), next(n) {}
    };

    Node** table;               // arreglo de punteros a listas
    size_t capacity;            // tamaño de la tabla
    size_t numElements;         // número total de elementos
    size_t maxCollisionK;       // k del PDF
    double maxFillFactor;       // 0.5
    HashPolicy hashFunction;

private:
    // Libera todos los nodos
    void clearBuckets() {
        for (size_t i = 0; i < capacity; ++i) {
            Node* current = table[i];
            while (current != nullptr) {
                Node* temp = current;
                current = current->next;
                delete temp;
            }
            table[i] = nullptr;
        }
    }

    // Inicializa tabla vacía
    void initTable(size_t cap) {
        capacity = cap;
        table = new Node*[capacity];
        for (size_t i = 0; i < capacity; ++i) {
            table[i] = nullptr;
        }
    }

    // Inserta nodo directamente en cabeza sin verificar fill factor
    void insertNodeAtHead(const Key& key, const Value& value) {
        size_t index = hashFunction(key, capacity);
        Node* newNode = new Node(key, value, table[index]);
        table[index] = newNode;
        ++numElements;
    }

    // Rehash: duplica capacidad y reubica todos los elementos
    void rehash() {
        size_t oldCapacity = capacity;
        Node** oldTable = table;

        initTable(capacity * 2);
        numElements = 0;

        for (size_t i = 0; i < oldCapacity; ++i) {
            Node* current = oldTable[i];
            while (current != nullptr) {
                insertNodeAtHead(current->key, current->value);
                Node* temp = current;
                current = current->next;
                delete temp;
            }
        }

        delete[] oldTable;
    }

    // Decide si, después de insertar uno más, se supera el fill factor
    bool needsRehashAfterNextInsertion() const {
        double projectedFill =
            static_cast<double>(numElements + 1) /
            static_cast<double>(capacity * maxCollisionK);

        return projectedFill > maxFillFactor;
    }

public:
    // -----------------------------
    // Constructor
    // -----------------------------
    explicit HashTable(size_t initialCapacity = 5,
                       size_t k = 3,
                       double maxFF = 0.5,
                       const HashPolicy& hp = HashPolicy())
        : table(nullptr),
          capacity(0),
          numElements(0),
          maxCollisionK(k),
          maxFillFactor(maxFF),
          hashFunction(hp) {
        if (initialCapacity == 0) {
            throw invalid_argument("La capacidad inicial debe ser > 0");
        }
        if (k == 0) {
            throw invalid_argument("k debe ser > 0");
        }
        if (maxFF <= 0.0) {
            throw invalid_argument("maxFillFactor debe ser > 0");
        }

        initTable(initialCapacity);
    }

    // -----------------------------
    // Destructor
    // -----------------------------
    ~HashTable() {
        clearBuckets();
        delete[] table;
    }

    // -----------------------------
    // Evitar copias accidentales
    // -----------------------------
    HashTable(const HashTable&) = delete;
    HashTable& operator=(const HashTable&) = delete;

    // -----------------------------
    // INSERT
    // Si la key existe, actualiza valor
    // Si no existe, inserta en cabeza
    // -----------------------------
    void insert(const Key& key, const Value& value) {
        size_t index = hashFunction(key, capacity);

        // Si ya existe, actualizamos
        Node* current = table[index];
        while (current != nullptr) {
            if (current->key == key) {
                current->value = value;
                return;
            }
            current = current->next;
        }

        // Verificamos rehash antes de insertar nuevo elemento
        if (needsRehashAfterNextInsertion()) {
            rehash();
            index = hashFunction(key, capacity);
        }

        // Inserción en cabeza
        Node* newNode = new Node(key, value, table[index]);
        table[index] = newNode;
        ++numElements;
    }

    // -----------------------------
    // SEARCH
    // Retorna puntero al valor o nullptr
    // -----------------------------
    Value* search(const Key& key) {
        size_t index = hashFunction(key, capacity);
        Node* current = table[index];

        while (current != nullptr) {
            if (current->key == key) {
                return &(current->value);
            }
            current = current->next;
        }
        return nullptr;
    }

    const Value* search(const Key& key) const {
        size_t index = hashFunction(key, capacity);
        Node* current = table[index];

        while (current != nullptr) {
            if (current->key == key) {
                return &(current->value);
            }
            current = current->next;
        }
        return nullptr;
    }

    // -----------------------------
    // REMOVE
    // Retorna true si eliminó
    // -----------------------------
    bool remove(const Key& key) {
        size_t index = hashFunction(key, capacity);
        Node* current = table[index];
        Node* prev = nullptr;

        while (current != nullptr) {
            if (current->key == key) {
                if (prev == nullptr) {
                    table[index] = current->next;
                } else {
                    prev->next = current->next;
                }
                delete current;
                --numElements;
                return true;
            }
            prev = current;
            current = current->next;
        }

        return false;
    }

    // -----------------------------
    // Utilidades
    // -----------------------------
    bool contains(const Key& key) const {
        return search(key) != nullptr;
    }

    size_t size() const {
        return numElements;
    }

    size_t getCapacity() const {
        return capacity;
    }

    size_t getK() const {
        return maxCollisionK;
    }

    double getFillFactor() const {
        // Fórmula del PDF:
        // FillFactor = #elements / (capacity * k)
        return static_cast<double>(numElements) /
               static_cast<double>(capacity * maxCollisionK);
    }

    double getMaxFillFactor() const {
        return maxFillFactor;
    }

    bool empty() const {
        return numElements == 0;
    }

    // Longitud de la lista en un bucket específico
    size_t bucketSize(size_t index) const {
        if (index >= capacity) {
            throw out_of_range("Índice de bucket fuera de rango");
        }

        size_t count = 0;
        Node* current = table[index];
        while (current != nullptr) {
            ++count;
            current = current->next;
        }
        return count;
    }

    // Imprimir tabla
    void print() const {
        cout << "-----------------------------------------\n";
        cout << "Capacity      : " << capacity << "\n";
        cout << "Elements      : " << numElements << "\n";
        cout << "k             : " << maxCollisionK << "\n";
        cout << "FillFactor    : " << getFillFactor() << "\n";
        cout << "MaxFillFactor : " << maxFillFactor << "\n";
        cout << "-----------------------------------------\n";

        for (size_t i = 0; i < capacity; ++i) {
            cout << "[" << i << "] -> ";
            Node* current = table[i];
            while (current != nullptr) {
                cout << "(" << current->key << ", " << current->value << ") -> ";
                current = current->next;
            }
            cout << "nullptr\n";
        }
        cout << "-----------------------------------------\n";
    }
};

// ============================================================
// DEMO
// ============================================================
int main() {
    cout << "=== HASH TABLE CON DIVISION HASH ===\n";
    HashTable<int, string, DivisionHash<int>> ht1(5, 3, 0.5);

    int keys[] = {2, 3, 6, 8, 10, 11, 15, 19, 20, 22, 25, 30};

    for (int key : keys) {
        ht1.insert(key, "valor_" + to_string(key));
        cout << "Insertado: " << key
             << " | capacity = " << ht1.getCapacity()
             << " | fillFactor = " << ht1.getFillFactor() << "\n";
    }

    ht1.print();

    if (auto p = ht1.search(19)) {
        cout << "Encontrado 19 -> " << *p << "\n";
    } else {
        cout << "19 no encontrado\n";
    }

    ht1.remove(19);
    cout << "Luego de eliminar 19:\n";
    ht1.print();

    cout << "\n=== HASH TABLE CON MULTIPLICATION HASH ===\n";
    MultiplicationHash<int> mh(0.6180339887);
    HashTable<int, string, MultiplicationHash<int>> ht2(5, 3, 0.5, mh);

    for (int key : keys) {
        ht2.insert(key, "v" + to_string(key));
    }
    ht2.print();

    cout << "\n=== HASH TABLE CON UNIVERSAL HASH ===\n";
    UniversalHash<int> uh(1000003);
    HashTable<int, string, UniversalHash<int>> ht3(5, 3, 0.5, uh);

    for (int key : keys) {
        ht3.insert(key, "u" + to_string(key));
    }
    ht3.print();

    cout << "Parámetros universal hash: "
         << "a=" << uh.getA()
         << ", b=" << uh.getB()
         << ", p=" << uh.getP() << "\n";

    return 0;
}
