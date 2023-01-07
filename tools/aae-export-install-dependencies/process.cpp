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


#include <QChar>
#include <QGuiApplication>
#include <QObject>
#include <QProcess>
#include <QQuickWindow>
#include <QString>
#include <QStringList>

#include "process.h"


Printout::Printout(QObject* parent): QObject(parent) {}

QString Printout::printout() {
    return m_printout;
}
void Printout::setPrintout(const QString& printout) {
    if(m_printout == printout)
        return;

    m_printout = printout;
    emit printoutChanged();
}
void Printout::appendPrintout(const QString& printout) {
    if(printout.length() == 0)
        return;

    m_printout += printout;
    emit printoutChanged();
}


Process::Process(QGuiApplication* app, Printout* parent): Printout(parent) {
    app_ = app;

    QObject::connect(&process, &QProcess::finished,
                     this, &Process::complete);
    QObject::connect(&process, &QProcess::errorOccurred,
                     this, &Process::error);
    QObject::connect(&process, &QProcess::readyReadStandardOutput,
                     this, &Process::readstdout);
    QObject::connect(&process, &QProcess::readyReadStandardError,
                     this, &Process::readstderr);
}


QString& Process::python() {
    return m_python;
}
QStringList& Process::packages() {
    return m_packages;
}
void Process::setPython(const QString& python) {
    m_python = python;
}
void Process::setPackages(const QStringList& packages) {
    m_packages = packages;
}


void Process::run() {
    if(step == 0) {
        step = 1;
        runensurepip();
    }
}
void Process::term() {
    if(process.state() != QProcess::NotRunning) {
        if(!is_termed) {
            is_termed = true;

            process.terminate();
            if(!process.waitForFinished(2000))
                process.kill();
        }
        else
            process.kill();
    }
}
void Process::complete(int exitCode, QProcess::ExitStatus exitStatus) {
    if(!is_termed) {
        if(step == 1) {
            if(exitCode != 0 || exitStatus != QProcess::NormalExit)
                complete_printout(exitCode, exitStatus);

            step = 2;
            runpipinstall();
        }
        else if(step == 2) {
            if(exitCode != 0 || exitStatus != QProcess::NormalExit)
                complete_printout(exitCode, exitStatus);

            else
                app_->quit();
        }
    }
}
void Process::complete_printout(int exitCode, QProcess::ExitStatus exitStatus) {
    QString printout;

    printout += QChar::LineFeed;
    printout += QStringLiteral("The command \"");
    printout += process.program();
    printout += QChar::Space;
    printout += process.arguments().join(QChar::Space);
    if(exitStatus != QProcess::NormalExit)
        printout += QStringLiteral("\" crashed");
    else { // exitCode != 0
        printout += QStringLiteral("\" returned a non-zero code: ");
        printout += QString::number(exitCode);
    }
    printout += QChar::LineFeed;
    printout += QChar::LineFeed;

    appendPrintout(printout);
}
void Process::error(QProcess::ProcessError error) {
    if(error == QProcess::FailedToStart) {
        QString printout;

        printout += QStringLiteral("The command \"");
        printout += process.program();
        printout += QChar::Space;
        printout += process.arguments().join(QChar::Space);
        printout += QStringLiteral("\" failed to start");
        printout += QChar::LineFeed;

        appendPrintout(printout);
    }
}


void Process::readstdout() {
    appendPrintout(process.readAllStandardOutput());
}
void Process::readstderr() {
    appendPrintout(process.readAllStandardError());
}


void Process::runensurepip() {
    QStringList arguments;
    arguments << "-m" << "ensurepip";
    process.setProgram(m_python);
    process.setArguments(arguments);

    process.start();
}
void Process::runpipinstall() {
    QStringList arguments;
    arguments << "-m" << "pip" << "install" << "--no-input";
    arguments += m_packages;
    process.setProgram(m_python);
    process.setArguments(arguments);

    process.start();
}

