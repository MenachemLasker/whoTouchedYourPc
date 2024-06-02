#include <iostream>
#include <winsock2.h>
#include <Ws2tcpip.h>
#include <fstream>
#include <opencv2/opencv.hpp>
#include <functional>
#include<openssl/sha.h>

#pragma comment(lib, "ws2_32.lib") // Winsock Library
using namespace cv;
using namespace std;


std::string hash_SHA256(const std::string& input) {
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256_CTX context;
    SHA256_Init(&context);
    SHA256_Update(&context, input.c_str(), input.length());
    SHA256_Final(hash, &context);

    std::stringstream ss;
    for (unsigned char i : hash) {
        ss << std::hex << std::setw(2) << std::setfill('0') << (int)i;
    }
    return ss.str();}


void setUser(SOCKET s) {
    std::string username, password;
    std::string hashedPass;
    char buffer;
    std::cout << "Enter your username: ";
    std::cin >> username;
    send(s, username.c_str(), username.size(), 0);
    recv(s, &buffer, sizeof(buffer), 0);
    bool uniqUser = buffer == '1';
    while (!uniqUser)
    {
        std::cout << "The username you ask is alredy exsist plese enter new username: ";
        std::cin >> username;
        send(s, username.c_str(), username.size(), 0);
        recv(s, &buffer, sizeof(buffer), 0);
        if (buffer == '1') uniqUser = true;
    }
    std::cout << "Enter your pasowrd: ";
    std::cin >> password;
    hashedPass =hash_SHA256(password);
    send(s, hashedPass.c_str(), hashedPass.length(), 0);
    }
void setId(SOCKET s) {
    char server_reply[1024];
    int recv_size;
    recv_size = recv(s, server_reply, sizeof(server_reply), 0);
    std::ofstream outfile("id.txt", std::ios::binary);
    outfile.write(server_reply, recv_size);
    outfile.close();
    setUser(s);
}
char* getId() {
    char buffer[1024];
    std::ifstream infile("id.txt", std::ios::binary);
    infile.read(buffer, sizeof(buffer));
    infile.close();
    return buffer;
}
bool isFileExist(const std::string& name) {
    std::ifstream file(name);
    return file.good();
}
void ShowImage(const Mat& image) {
    // הצגת התמונה בחלון
    imshow("Image", image);

    // המתנה ללחיצת מקש
    waitKey(0);
}
bool TakeAndSavePicture(const std::string& filename) {
    // פותח את המצלמה
    VideoCapture camera(0);
    if (!camera.isOpened()) {
        std::cerr << "Could not open camera!" << std::endl;
        return false;
    }

    // קורא פריים מהמצלמה
    Mat frame;
    camera >> frame;

    // בודק אם קריאה לפריים הצליחה
    if (frame.empty()) {
        std::cerr << "Could not read frame from camera!" << std::endl;
        return false;
    }

    // כותב את התמונה לקובץ
    imwrite(filename, frame);

    // סוגר את המצלמה
    camera.release();

    return true;
}
int sendImage(SOCKET s, const char* image_path) {
    std::ifstream picture;
    picture.open(image_path, std::ios::binary);

    // Get the size of the file
    picture.seekg(0, std::ios::end);
    size_t size = picture.tellg();
    picture.seekg(0, std::ios::beg);

    // Allocate memory for the file buffer
    char* buffer = new char[size];

    // Read the file into the buffer
    picture.read(buffer, size);

    // Send the buffer to the server
    send(s, buffer, size, 0);

    // Clean up
    delete[] buffer;
    picture.close();
    return 0;
}
int main() {
    /*bool exitLoop = false;
    POINT cursorPos, lastCursorPos;
    // אתחול המיקום הקודם של הסמן
    GetCursorPos(&lastCursorPos);
    while (!exitLoop) {
        // בדיקה אם כפתור עכבר נלחץ
        if (GetAsyncKeyState(VK_LBUTTON) & 0x8000) {
            exitLoop = true;
        }

        // בדיקה אם מקש כלשהו במקלדת נלחץ
        for (int key = 8; key <= 190; key++) {
            if (GetAsyncKeyState(key) & 0x8000) {
                exitLoop = true;
                break;
            }
        }
        // עכבר
        GetCursorPos(&cursorPos);
        if (cursorPos.x != lastCursorPos.x || cursorPos.y != lastCursorPos.y) {
            exitLoop = true;
        }
        Sleep(50);
    }*/
    WSADATA wsa;
    SOCKET s;
    struct sockaddr_in server;
    // Initialize Winsock
    WSAStartup(MAKEWORD(2, 2), &wsa);

    // Create a socket
    s = socket(AF_INET, SOCK_STREAM, 0);
    server.sin_family = AF_INET;
    server.sin_port = htons(5010);

    InetPton(AF_INET, L"127.0.0.1", &server.sin_addr.s_addr);

     // Connect to remote server
    connect(s, (struct sockaddr*)&server, sizeof(server));
    bool haveId = isFileExist("id.txt");
    char haveIdValue = haveId ? '1' : '0'; // המרה של הערך הבוליאני לתו
    send(s, &haveIdValue, sizeof(haveIdValue), 0); // שליחת התו
    if (! haveId)
    {
        setId(s);
        return 0;
    } 
    send(s, getId(), 1024, 0);
    // שם הקובץ
    const std::string filename = "image.jpg";
    TakeAndSavePicture(filename);
    Mat image = imread(filename);
    //ShowImage(image);
    std::cout << "Connected\n";

    // Send the image
    sendImage(s, "image.jpg");

    std::cout << "Image Sent\n";

    closesocket(s);
    WSACleanup();
    return 0;
}

