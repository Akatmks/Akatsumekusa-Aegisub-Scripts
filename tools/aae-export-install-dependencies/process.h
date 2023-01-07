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


#ifndef PROCESS_H
#define PROCESS_H


#include <QGuiApplication>
#include <QObject>
#include <QProcess>
#include <QQmlEngine>
#include <QQuickWindow>
#include <QString>
#include <QStringList>


class Printout: public QObject {
    Q_OBJECT
    Q_PROPERTY(QString printout READ printout WRITE setPrintout NOTIFY printoutChanged)
    QML_ELEMENT
    QML_UNCREATABLE("")

public:
    explicit Printout(QObject* parent = nullptr);

    QString printout();
    void setPrintout(const QString& printout);
    void appendPrintout(const QString& printout);

signals:
    void printoutChanged();

private:
    QString m_printout;
};


class Process: public Printout {
    Q_OBJECT
    QML_ELEMENT
    QML_UNCREATABLE("")

public:
    explicit Process(QGuiApplication* app, Printout* parent = nullptr);

    QString& python();
    QStringList& packages();
    void setPython(const QString& python);
    void setPackages(const QStringList& packages);

    Q_INVOKABLE void run();
    Q_INVOKABLE void term();
public slots:
    void complete(int exitCode, QProcess::ExitStatus exitStatus = QProcess::NormalExit);
private:
    void complete_printout(int exitCode, QProcess::ExitStatus exitStatus);
public slots:
    void error(QProcess::ProcessError error);

    void readstdout();
    void readstderr();

private:
    QProcess process;
    int step = 0;

    void runensurepip();
    void runpipinstall();
    QString m_python;
    QStringList m_packages;

    QGuiApplication* app_;
    bool is_termed = false;
};


#endif // PROCESS_H

