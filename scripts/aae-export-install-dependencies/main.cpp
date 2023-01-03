/* aae-export-install-dependencies
 * Copyright (c) Akatsumekusa and contributors
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */


#include <QCommandLineParser>
#include <QCoreApplication>
#include <QFont>
#include <QGuiApplication>
#include <QObject>
#include <QQmlApplicationEngine>
#include <QQmlContext>
#include <QString>
#include <QStringList>

#include "main.h"
#include "process.h"


int main(int argc, char** argv) {
#if QT_VERSION < QT_VERSION_CHECK(6, 0, 0)
    QCoreApplication::setAttribute(Qt::AA_EnableHighDpiScaling);
#endif
    QGuiApplication app(argc, argv);

    main_setInformation(app);
    main_parseArg(app);

    main_setFont(app);

    QQmlApplicationEngine engine;
    const QUrl url(QStringLiteral("qrc:/main.qml"));
    QObject::connect(&engine, &QQmlApplicationEngine::objectCreated,
                     &app, [url](QObject* obj, const QUrl& objUrl) {
                         if (!obj && url == objUrl)
                             QCoreApplication::exit(-1);
                     }, Qt::QueuedConnection);
    engine.load(url);

    main_setPrintout(engine);

    return app.exec();
}


void main_setInformation(QGuiApplication& app) {
    app.setApplicationName("aae-export-install-dependencies");
    app.setApplicationVersion("1.0");
}

void main_parseArg(QGuiApplication& app) {
    QCommandLineParser parser;

    parser.addHelpOption();
    parser.addVersionOption();
    parser.addPositionalArgument("python", "Path to Python binary.");
    parser.addPositionalArgument("packages ...", "Pip packages to install.");

    parser.process(app);

    const QStringList& args = parser.positionalArguments();
    if(args.size() < 2)
        parser.showHelp(-1);

    python = args.at(0);
    packages = args.sliced(1);
}


void main_setFont(QGuiApplication& app) {
    QFont Font;
    Font.setStyleHint(QFont::Monospace);
    Font.setFamily(Font.defaultFamily());
    app.setFont(Font);
}

void main_setPrintout(QQmlApplicationEngine& engine) {
    Printout printout;
    engine.rootContext()->setContextProperty("printout", &printout);
}

