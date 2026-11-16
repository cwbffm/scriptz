#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <commdlg.h>
#include <filesystem>
#include <fstream>
#include <iterator>
#include <string>
#include <vector>

namespace {
HWND textView = nullptr;
HBITMAP image = nullptr;
const int OPEN_REPORT = 101;
const int OPEN_BMP = 102;
const int TOP = 58;

std::wstring readUtf8(const std::filesystem::path& path) {
    std::ifstream f(path, std::ios::binary | std::ios::ate);
    if (!f) return L"Falha ao abrir arquivo.";
    auto bytes = f.tellg();
    if (bytes <= 0) return L"Arquivo vazio.";
    if (bytes > 16 * 1024 * 1024) return L"Arquivo muito grande para o visualizador.";
    f.seekg(0);
    std::string data(static_cast<size_t>(bytes), '\0');
    if (!f.read(data.data(), static_cast<std::streamsize>(data.size())))
        return L"Falha ao ler arquivo.";
    // Strip UTF-8 BOM.
    if (data.size() >= 3 && static_cast<unsigned char>(data[0]) == 0xef &&
        static_cast<unsigned char>(data[1]) == 0xbb &&
        static_cast<unsigned char>(data[2]) == 0xbf) {
        data.erase(0, 3);
    }
    int count = MultiByteToWideChar(CP_UTF8, MB_ERR_INVALID_CHARS,
                                   data.data(), static_cast<int>(data.size()), nullptr, 0);
    if (count <= 0) return L"Relatorio nao esta em UTF-8 valido.";
    std::wstring result(static_cast<size_t>(count), L'\0');
    MultiByteToWideChar(CP_UTF8, MB_ERR_INVALID_CHARS, data.data(),
                        static_cast<int>(data.size()), result.data(), count);
    return result;
}

bool chooseFile(HWND window, wchar_t* output, const wchar_t* filter) {
    output[0] = L'\0';
    OPENFILENAMEW dialog{};
    dialog.lStructSize = sizeof(dialog);
    dialog.hwndOwner = window;
    dialog.lpstrFile = output;
    dialog.nMaxFile = MAX_PATH;
    dialog.lpstrFilter = filter;
    dialog.Flags = OFN_FILEMUSTEXIST | OFN_PATHMUSTEXIST;
    return GetOpenFileNameW(&dialog) == TRUE;
}

void openReport(HWND window) {
    wchar_t path[MAX_PATH]{};
    if (!chooseFile(window, path, L"Relatorios\0*.txt;*.json;*.asm\0Todos\0*.*\0")) return;
    if (image) {
        DeleteObject(image);
        image = nullptr;
    }
    std::wstring contents = readUtf8(path);
    SetWindowTextW(textView, contents.c_str());
    ShowWindow(textView, SW_SHOW);
    InvalidateRect(window, nullptr, TRUE);
}

void openBmp(HWND window) {
    wchar_t path[MAX_PATH]{};
    if (!chooseFile(window, path, L"Bitmap\0*.bmp\0Todos\0*.*\0")) return;
    HBITMAP next = static_cast<HBITMAP>(LoadImageW(
        nullptr, path, IMAGE_BITMAP, 0, 0, LR_LOADFROMFILE | LR_CREATEDIBSECTION
    ));
    if (!next) {
        MessageBoxW(window, L"Bitmap invalido.", L"CrashNative", MB_ICONERROR);
        return;
    }
    if (image) DeleteObject(image);
    image = next;
    ShowWindow(textView, SW_HIDE);
    InvalidateRect(window, nullptr, TRUE);
}

LRESULT CALLBACK windowProc(HWND window, UINT message, WPARAM wp, LPARAM lp) {
    switch (message) {
    case WM_CREATE: {
        HINSTANCE instance = reinterpret_cast<LPCREATESTRUCTW>(lp)->hInstance;
        CreateWindowW(L"BUTTON", L"Abrir relatorio", WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
                      12, 12, 160, 34, window, reinterpret_cast<HMENU>(OPEN_REPORT), instance, nullptr);
        CreateWindowW(L"BUTTON", L"Visualizar tela de carregamento", WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
                      185, 12, 280, 34, window, reinterpret_cast<HMENU>(OPEN_BMP), instance, nullptr);
        textView = CreateWindowExW(
            WS_EX_CLIENTEDGE, L"EDIT",
            L"CrashNative Inspector v0.1\r\n\r\n"
            L"Abra o summary.txt / analysis.json ou o BMP exportado do NSD.\r\n"
            L"Este aplicativo NAO executa o jogo e ainda NAO renderiza fases em 3D.",
            WS_CHILD | WS_VISIBLE | WS_VSCROLL | WS_HSCROLL | ES_MULTILINE |
            ES_READONLY | ES_AUTOVSCROLL | ES_AUTOHSCROLL,
            12, TOP, 860, 510, window, nullptr, instance, nullptr);
        SendMessageW(textView, WM_SETFONT,
                     reinterpret_cast<WPARAM>(GetStockObject(ANSI_FIXED_FONT)), TRUE);
        return 0;
    }
    case WM_SIZE: {
        int w = LOWORD(lp), h = HIWORD(lp);
        if (textView) MoveWindow(textView, 12, TOP, w > 24 ? w-24 : 1,
                                 h > TOP+12 ? h-TOP-12 : 1, TRUE);
        InvalidateRect(window, nullptr, FALSE);
        return 0;
    }
    case WM_COMMAND:
        if (LOWORD(wp) == OPEN_REPORT) openReport(window);
        else if (LOWORD(wp) == OPEN_BMP) openBmp(window);
        return 0;
    case WM_PAINT: {
        PAINTSTRUCT paint{};
        HDC dc = BeginPaint(window, &paint);
        if (image) {
            BITMAP bm{};
            GetObjectW(image, sizeof(bm), &bm);
            RECT bounds{};
            GetClientRect(window, &bounds);
            int availableW = bounds.right-24;
            int availableH = bounds.bottom-TOP-12;
            if (bm.bmWidth > 0 && bm.bmHeight > 0 && availableW > 0 && availableH > 0) {
                double scaleW = static_cast<double>(availableW)/bm.bmWidth;
                double scaleH = static_cast<double>(availableH)/bm.bmHeight;
                double scale = scaleW < scaleH ? scaleW : scaleH;
                int destW = static_cast<int>(bm.bmWidth*scale);
                int destH = static_cast<int>(bm.bmHeight*scale);
                HDC src = CreateCompatibleDC(dc);
                HGDIOBJ previous = SelectObject(src, image);
                SetStretchBltMode(dc, HALFTONE);
                StretchBlt(dc, (bounds.right-destW)/2, TOP+(availableH-destH)/2,
                           destW, destH, src, 0, 0, bm.bmWidth, bm.bmHeight, SRCCOPY);
                SelectObject(src, previous);
                DeleteDC(src);
            }
        }
        EndPaint(window, &paint);
        return 0;
    }
    case WM_DESTROY:
        if (image) DeleteObject(image);
        PostQuitMessage(0);
        return 0;
    }
    return DefWindowProcW(window, message, wp, lp);
}
}  // namespace

int WINAPI wWinMain(HINSTANCE instance, HINSTANCE, PWSTR, int show) {
    WNDCLASSW wc{};
    wc.hInstance = instance;
    wc.lpfnWndProc = windowProc;
    wc.lpszClassName = L"CrashNativeWindow";
    wc.hCursor = LoadCursorW(nullptr, IDC_ARROW);
    wc.hbrBackground = reinterpret_cast<HBRUSH>(COLOR_WINDOW+1);
    if (!RegisterClassW(&wc)) return 1;
    HWND window = CreateWindowExW(0, wc.lpszClassName,
        L"CrashNative - PS1 Resource Inspector", WS_OVERLAPPEDWINDOW,
        CW_USEDEFAULT, CW_USEDEFAULT, 960, 700,
        nullptr, nullptr, instance, nullptr);
    if (!window) return 1;
    ShowWindow(window, show);
    MSG msg{};
    while (GetMessageW(&msg, nullptr, 0, 0)>0) {
        TranslateMessage(&msg);
        DispatchMessageW(&msg);
    }
    return static_cast<int>(msg.wParam);
}
